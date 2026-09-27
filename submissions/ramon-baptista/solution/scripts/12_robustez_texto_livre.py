from __future__ import annotations

import csv, hashlib, json, math, re, sys, unicodedata
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[2]
OUT = ROOT / "outputs" / "robustez"
sys.path.insert(0, str(ROOT / "src"))
from ticket_classifier.core import load_data, load_verified_model, route, routing_thresholds
from ticket_classifier.language import load_language_guard
from ticket_classifier.out_of_scope import OUT_OF_SCOPE_PATTERNS
from ticket_classifier.service import MAX_TICKET_LENGTH, classify_ticket

CLASSES = ["Access", "Administrative rights", "HR Support", "Hardware", "Internal Project", "Miscellaneous", "Purchase", "Storage"]
VOCAB = {
 "Access": (["VPN", "payroll portal", "corporate email", "timesheet", "intranet"], ["rejects my password", "locks me out", "denies my login", "ends my session"]),
 "Administrative rights": (["analytics client", "graphics driver", "audit utility", "firewall settings", "Java console"], ["requires administrator approval", "is blocked by policy", "needs elevated permission", "requests privileged access"]),
 "HR Support": (["salary record", "vacation balance", "health benefit", "job title", "tax withholding"], ["shows the wrong value", "needs correction", "is missing an update", "disagrees with my documents"]),
 "Hardware": (["laptop screen", "office monitor", "wireless keyboard", "desk mouse", "network printer"], ["has stopped working", "is physically damaged", "needs replacement", "shows a hardware fault"]),
 "Internal Project": (["Orion migration", "Atlas launch", "Phoenix rollout", "Nimbus pilot", "Mercury program"], ["needs a shared workspace", "requires technical setup", "needs the team added", "requires deployment support"]),
 "Miscellaneous": (["office directory", "IT opening hours", "support policy", "help desk location", "onboarding guide"], ["is unclear to me", "needs a general explanation", "is not listed online", "requires guidance"]),
 "Purchase": (["noise cancelling headset", "conference webcam", "design license", "laptop dock", "office phone"], ["needs a purchase request", "should be ordered by procurement", "requires buying approval", "must be acquired for work"]),
 "Storage": (["OneDrive account", "SharePoint library", "network folder", "email mailbox", "project drive"], ["has reached its quota", "needs more capacity", "is out of space", "requires a storage increase"]),
}
SHORT = {
 "Access": ["VPN", "email", "intranet", "timesheet", "portal", "account", "login"], "Administrative rights": ["admin", "elevation", "privileges", "administrator", "sudo", "permission", "rights"],
 "HR Support": ["payroll", "vacation", "benefits", "salary", "title", "tax", "leave"], "Hardware": ["laptop", "monitor", "keyboard", "mouse", "printer", "screen", "charger"],
 "Internal Project": ["Orion", "Atlas", "Phoenix", "Nimbus", "Mercury", "project", "rollout"], "Miscellaneous": ["directory", "policy", "guidance", "helpdesk", "hours", "onboarding", "information"],
 "Purchase": ["headset", "webcam", "license", "dock", "phone", "adapter", "tablet"], "Storage": ["OneDrive", "SharePoint", "folder", "mailbox", "drive", "quota", "storage"],
}
STATES = ["blocked", "unavailable", "problem", "request", "needed", "failed", "urgent", "incorrect", "missing", "full", "broken", "approval", "support"]
MIX = ["No puedo", "Necesito ayuda para", "Por favor necesito", "Mi equipo dice que", "Hoje não consigo", "Preciso resolver", "Pode ajudar com", "Meu colega reportou que", "La oficina informa que", "Quiero corregir", "Não funciona", "Tenemos un problema con", "Favor verificar"]
OOS_KEYWORDS = {
 "refund": ["a duplicate order", "a returned product", "a cancelled booking", "my original card"], "billing": ["a statement charge", "an invoice address", "my subscription cycle", "this month dispute"],
 "charged": ["twice for one order", "after cancelling service", "the wrong amount", "for a returned item"], "delivery": ["past its promised date", "sent to a wrong address", "with damaged contents", "that never arrived"],
 "shipment": ["with frozen tracking", "held by the carrier", "missing one package", "routed to another city"], "cancel subscription": ["before renewal", "and confirm the end date", "because I no longer use it", "without another fee"],
 "cancel my order": ["before dispatch", "because it was a mistake", "and release the card hold", "because the address is wrong"], "complaint": ["about rude store service", "about a damaged parcel", "about repeated sales calls", "about the return process"],
 "chargeback": ["for an unauthorized purchase", "evidence for my bank", "status after the dispute", "deadline for this transaction"], "complain": ["about misleading pricing", "about courier behavior", "about a missing refund", "about cancellation handling"],
}
OOS_PT = [
 "Preciso de reembolso por uma compra duplicada", "Quero reembolso depois de devolver o produto", "A cobrança no meu cartão está errada", "Fui cobrado mesmo após cancelar o serviço", "Minha entrega passou da data prometida", "A entrega foi enviada ao endereço errado", "O rastreamento do pedido não muda há uma semana", "Meu pedido chegou com um item faltando", "Quero cancelar minha assinatura antes da renovação", "Preciso cancelar meu pedido antes do envio", "Tenho uma reclamação sobre o atendimento da loja", "Quero reclamar das ligações de vendas", "A fatura mostra um valor que não reconheço", "Solicito cancelamento e estorno da compra", "A transportadora perdeu minha encomenda", "O produto devolvido ainda não foi reembolsado", "Recebi cobrança em duplicidade neste mês", "Minha assinatura continuou ativa após o cancelamento", "A entrega veio danificada e quero devolução", "O pedido aparece entregue mas não recebi", "Preciso corrigir o endereço de entrega", "Quero contestar uma compra não autorizada", "A loja recusou a devolução dentro do prazo", "O cupom não foi aplicado na compra", "Meu pagamento foi aprovado mas o pedido sumiu", "Quero trocar o produto recebido por engano", "O valor do frete foi cobrado incorretamente", "A parcela da compra veio com juros indevidos", "Não recebi confirmação do estorno", "A transportadora marcou uma tentativa inexistente", "Quero encerrar o plano e receber confirmação", "O vendedor prometeu um desconto não aplicado", "Minha encomenda foi enviada para outra cidade", "Preciso alterar a forma de pagamento do pedido", "O prazo de devolução informado está incorreto", "A garantia comercial não foi respeitada", "Quero registrar queixa sobre propaganda enganosa", "O pacote chegou aberto e sem o produto", "A renovação automática ocorreu sem aviso", "Preciso da segunda via da nota fiscal da compra"]

def norm(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    return " ".join(re.findall(r"[^\W\d_]+", "".join(c for c in text if not unicodedata.combining(c))))

def typo(text, variant):
    words = text.split(); choices = [i for i,w in enumerate(words) if len(re.sub(r"\W", "", w)) >= 6]
    p = choices[variant % len(choices)]; chars = list(words[p]); q = max(1, min(len(chars)-2, len(chars)//2)); chars[q],chars[q+1]=chars[q+1],chars[q]; words[p]="".join(chars)
    return " ".join(words)

def make_cases():
    rows=[]
    def add(g,t,l,lang="ingles"): rows.append({"case_id":f"R{len(rows)+1:04d}","group":g,"language":lang,"text":t,"expected_label":l,"origin":"sintetico_gerado_por_IA"})
    for label in CLASSES:
        objects, states = VOCAB[label]; base=[f"The {o} {s}." for o in objects for s in states]
        for text in base: add("reformulacoes_8_filas",text,label)
        for i,text in enumerate(base): add("erros_de_digitacao",typo("Please assist because "+text.lower(),i),label)
        for i in range(13):
            add("textos_curtos",f"{SHORT[label][i%7]} {STATES[i]}",label)
            add("mistura_de_idiomas",f"{MIX[i]} {objects[i%5]} because it {states[i%4]}",label,"misto")
    for keyword, tails in OOS_KEYWORDS.items():
        for opener in ["Please review", "I need help with", "Can someone resolve", "The customer reported", "Our store received", "I am contacting support about", "Please investigate", "The account shows", "I want assistance with", "The sales team escalated"]:
            for tail in tails: add("fora_do_escopo",f"{opener} {keyword} {tail}.","fora_do_escopo")
    for text in OOS_PT:
        for context in ["na compra desta semana", "no pedido feito pelo aplicativo", "na conta usada pela família", "durante o atendimento da loja", "na transação mais recente", "no contrato do cliente"]:
            add("fora_do_escopo",f"{text} {context}.","fora_do_escopo","portugues")
    ns=[norm(r["text"]) for r in rows]; dup=pd.Series(ns).duplicated(False)
    if dup.any(): raise AssertionError(f"Repetição normalizada: {pd.Series(ns)[dup].tolist()[:5]}")
    counts=pd.Series([r["group"] for r in rows]).value_counts()
    if (counts<100).any(): raise AssertionError(f"Grupo abaixo de 100: {counts.to_dict()}")
    return rows

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def wilson(k,n,z=1.959963984540054):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0,c-h),min(1,c+h)
def outcome(row,result):
    if not result["automatic"]: return "desviado_para_pessoa"
    return "direto_certo" if row["expected_label"]!="fora_do_escopo" and result["category"]==row["expected_label"] else "direto_fila_errada"

def evaluate(rows,model,manifest,guard):
    out=[]
    for row in rows:
        result=classify_ticket(row["text"],model,manifest,guard,False,False); normalized=norm(row["text"])
        out.append({**row,"texto_normalizado":normalized,"split_correcao":"calibracao" if int(hashlib.sha256(normalized.encode()).hexdigest()[:8],16)%2==0 else "medicao","predicted_label":result["category"],"score_nao_calibrado":result["score"],"faixa_original":result["original_band"],"protecao_idioma":result["language_diversion"],"resultado_atual":outcome(row,result)})
    return pd.DataFrame(out)

def summarize(df,col,by_language=False):
    ans=[]; keys=["group","language"] if by_language else ["group"]
    for values,part in df.groupby(keys,sort=False):
        values=values if isinstance(values,tuple) else (values,); row={"grupo":values[0],"n":len(part),"n_frases_distintas":part.texto_normalizado.nunique()}
        if by_language: row["idioma"]=values[1]
        for name in ["direto_fila_errada","direto_certo","desviado_para_pessoa"]:
            k=int((part[col]==name).sum()); row[name]={"n":k,"taxa":k/len(part),"ic95_wilson":list(wilson(k,len(part)))}
        ans.append(row)
    return ans

def calibrate(df):
    cal=df[(df.group=="fora_do_escopo")&(df.split_correcao=="calibracao")]; selected=[]; audit=[]
    for pattern in OUT_OF_SCOPE_PATTERNS:
        hit=cal.text.str.contains(pattern,case=False,regex=True); errors=int((hit&(cal.resultado_atual=="direto_fila_errada")).sum())
        if errors>=2: selected.append(pattern)
        audit.append({"padrao":pattern,"casos":int(hit.sum()),"erros_automaticos":errors,"selecionado":errors>=2})
    if not selected: raise AssertionError("Nenhum padrão selecionado na calibração")
    return selected,{"n_calibracao_oos":len(cal),"n_ingles":int((cal.language=="ingles").sum()),"n_portugues":int((cal.language=="portugues").sum()),"criterio":"padrão em pelo menos 2 erros automáticos fora do escopo na calibração","padroes":audit}

def apply_correction(df,patterns):
    regex=re.compile("|".join(f"(?:{p})" for p in patterns),re.I); df=df.copy(); df["correcao_fora_escopo_acionada"]=df.text.map(lambda x:bool(regex.search(x))); df["resultado_correcao"]=df.resultado_atual; df.loc[df.correcao_fora_escopo_acionada,"resultado_correcao"]="desviado_para_pessoa"; return df

def base1(model,manifest,guard,patterns):
    texts=pd.read_csv(REPO_ROOT/"data"/"customer_support_tickets.csv",usecols=["Ticket Description"])["Ticket Description"].fillna("").astype(str)
    clean=texts.str.replace("{product_purchased}"," ",regex=False).str.replace(r"\s+"," ",regex=True).str.strip()
    before=[classify_ticket(x,model,manifest,guard,False,False) for x in clean]
    after=[classify_ticket(x,model,manifest,guard,False,True) for x in clean]
    before_auto=pd.Series([r["automatic"] for r in before],index=clean.index)
    after_auto=pd.Series([r["automatic"] for r in after],index=clean.index)
    pattern_counts=[]
    for pattern in patterns:
        hit=clean.str.contains(pattern,case=False,regex=True)
        pattern_counts.append({"padrao":pattern,"disparos_n":int(hit.sum()),"bloqueios_de_automaticos_n":int((hit&before_auto).sum())})
    examples=[]
    for idx in clean.index[after_auto][:10]:
        examples.append({"ticket_linha":int(idx)+1,"texto":clean.loc[idx],"fila_sugerida":after[idx]["category"],"score_nao_calibrado":after[idx]["score"]})
    k_before=int(before_auto.sum()); k_after=int(after_auto.sum()); n=len(texts)
    return {"n":n,"placeholder_n":int(texts.str.contains("{product_purchased}",regex=False).sum()),
            "antes":{"direto_n":k_before,"direto_taxa":k_before/n,"ic95_wilson":list(wilson(k_before,n))},
            "depois":{"direto_n":k_after,"direto_taxa":k_after/n,"ic95_wilson":list(wilson(k_after,n))},
            "bloqueados_n":k_before-k_after,"padroes":pattern_counts,"exemplos_ainda_direto":examples,
            "metodo":"proporção de decisões automáticas antes e depois da barreira congelada, após proteção de idioma",
            "fundamento":"mede generalização da barreira em outro domínio, sem usar a Base 1 para recalibrar"}

def automatic_error_by_group(df,col):
    rows=[]
    for group,part in df.groupby("group",sort=False):
        wrong=int((part[col]=="direto_fila_errada").sum()); right=int((part[col]=="direto_certo").sum()); n_auto=wrong+right
        rows.append({"grupo":group,"errado_n":wrong,"certo_n":right,"encaminhados_n":n_auto,
                     "taxa_erro":wrong/n_auto if n_auto else None,
                     "ic95_wilson":list(wilson(wrong,n_auto)) if n_auto else None})
    return rows

def frozen_cost(model,manifest,guard,patterns):
    frozen=pd.read_csv(ROOT/"artifacts"/"frozen_test.csv"); source=load_data()[["record_id","Document"]]; joined=frozen[["record_id"]].merge(source,on="record_id",validate="one_to_one"); low,high=routing_thresholds(manifest); official=route(model.predict_proba(joined.Document).max(axis=1),low,high)=="alta"; eligible=(joined.Document.str.len()<=MAX_TICKET_LENGTH).to_numpy(); lang=pd.Series(False,index=joined.index); lang.loc[eligible]=joined.loc[eligible,"Document"].map(lambda x:classify_ticket(x,model,manifest,guard,False,False)["language_diversion"]); lang=lang.to_numpy(); service=official&eligible&~lang; regex=re.compile("|".join(f"(?:{p})" for p in patterns),re.I); hits=joined.Document.map(lambda x:bool(regex.search(x))).to_numpy(); after=service&~hits; n=len(frozen)
    correct=(frozen.expected_label==frozen.expected_prediction).to_numpy(); high_n=int(official.sum()); high_wrong=int((official&~correct).sum())
    return {"n":n,"cobertura_oficial_faixa_alta_n":high_n,"cobertura_oficial_faixa_alta_taxa":official.mean(),"faixa_alta_certo_n":int((official&correct).sum()),"faixa_alta_errado_n":high_wrong,"faixa_alta_taxa_erro":high_wrong/high_n,"faixa_alta_erro_ic95_wilson":list(wilson(high_wrong,high_n)),"acima_limite_na_faixa_alta_n":int((official&~eligible).sum()),"desvios_idioma_na_faixa_alta_elegivel_n":int((official&eligible&lang).sum()),"automatico_servico_atual_n":int(service.sum()),"automatico_servico_atual_taxa":service.mean(),"automatico_com_correcao_n":int(after.sum()),"automatico_com_correcao_taxa":after.mean(),"queda_correcao_n":int(service.sum()-after.sum()),"queda_correcao_pp":100*(service.sum()-after.sum())/n,"consistencia":int(official.sum())-int((official&~eligible).sum())-int((official&eligible&lang).sum())==int(service.sum())}

def pct(x,d=1): return f"{100*x:.{d}f}%".replace(".",",")
def metric(row,key):
    x=row[key]; return f"{x['n']}/{row['n']} = {pct(x['taxa'])} [{pct(x['ic95_wilson'][0])}; {pct(x['ic95_wilson'][1])}]"

def report(current,oos_lang,corrected,b1,cost,cal,h,patterns,error_rows):
    a=b1["antes"]; d=b1["depois"]
    L=["# Robustez com texto livre","","## Teste principal: Base 1","",
       f"Antes da barreira, **{a['direto_n']}/{b1['n']} = {pct(a['direto_taxa'])} (n={b1['n']}; IC95% de Wilson {pct(a['ic95_wilson'][0])}–{pct(a['ic95_wilson'][1])})** iriam direto. Com a mesma barreira, sem ajuste, ainda vão direto **{d['direto_n']}/{b1['n']} = {pct(d['direto_taxa'])} (n={b1['n']}; IC95% {pct(d['ic95_wilson'][0])}–{pct(d['ic95_wilson'][1])})**.","",
       "A barreira **não generaliza** para a Base 1: ela bloqueia apenas uma parcela pequena das decisões automáticas em tickets de outro domínio. A Base 1 não será usada para criar ou recalibrar regra.","",
       f"Método: remoção literal de `{{product_purchased}}` nas {b1['placeholder_n']} descrições e aplicação do serviço completo antes/depois dos cinco padrões congelados. Wilson bilateral de 95% foi escolhido por manter limites válidos; pressupõe tickets independentes. Isto mede exposição, não acurácia, porque a Base 1 não tem rótulos compatíveis com as oito filas.","","### Padrões que dispararam","","| Padrão congelado | Disparos na Base 1 | Automáticos bloqueados |","|---|---:|---:|"]
    for r in b1["padroes"]: L.append(f"| `{r['padrao']}` | {r['disparos_n']} (n={b1['n']}) | {r['bloqueios_de_automaticos_n']} (n={a['direto_n']}) |")
    L.append("")
    L.append(f"Os bloqueios por padrão somam {sum(r['bloqueios_de_automaticos_n'] for r in b1['padroes'])}, mas são {b1['bloqueados_n']} tickets únicos (n={a['direto_n']} antes da barreira), porque dois tickets acionaram mais de um padrão. Método: contagem por padrão e união por ticket; fundamento: evitar dupla contagem.")
    L += ["","### Dez tickets que ainda passam direto","","| Linha | Fila sugerida | Score não calibrado | Texto |","|---:|---|---:|---|"]
    for r in b1["exemplos_ainda_direto"]: L.append(f"| {r['ticket_linha']} | {r['fila_sugerida']} | {r['score_nao_calibrado']:.3f} | {r['texto'].replace('|','\\|')} |")
    L += ["","## Evidência complementar: sintéticos","","Os sintéticos são estresse controlado do mesmo gerador, não prova de generalização nem estimativa operacional. Rótulos e hash foram gravados antes da inferência. Como todos os grupos têm menos de 100 encaminhados, as taxas condicionais são exploratórias e não sustentam recomendação; o grupo misto também tem n<30.","",
          f"No teste congelado, a faixa alta acerta **{cost['faixa_alta_certo_n']}/{cost['cobertura_oficial_faixa_alta_n']} = {pct(1-cost['faixa_alta_taxa_erro'],2)} (n={cost['cobertura_oficial_faixa_alta_n']})**; o erro é **{cost['faixa_alta_errado_n']}/{cost['cobertura_oficial_faixa_alta_n']} = {pct(cost['faixa_alta_taxa_erro'],2)} (IC95% {pct(cost['faixa_alta_erro_ic95_wilson'][0])}–{pct(cost['faixa_alta_erro_ic95_wilson'][1])})**. Método: errado ÷ (errado + certo) apenas na faixa alta; fundamento: mede o risco condicional entre encaminhados.","","| Grupo sintético | Errado ÷ encaminhados com barreira | IC95% de Wilson |","|---|---:|---:|"]
    for r in error_rows:
        interval=r["ic95_wilson"]
        if r["encaminhados_n"]:
            L.append(f"| {r['grupo']} | {r['errado_n']}/{r['encaminhados_n']} = {pct(r['taxa_erro'])} | {pct(interval[0])}–{pct(interval[1])} (n={r['encaminhados_n']}) |")
        else:
            L.append(f"| {r['grupo']} | não estimável: 0 encaminhados | não aplicável (n=0) |")
    L += ["","## Rastreabilidade","",f"- `casos_rotulados.csv`, SHA-256 `{h}`.","- Nenhum modelo, split, teste congelado, limiar, número oficial ou padrão foi alterado."]
    return "\n".join(L)+"\n"

def main():
    OUT.mkdir(parents=True,exist_ok=True); rows=make_cases(); path=OUT/"casos_rotulados.csv"
    with path.open("w",newline="",encoding="utf-8-sig") as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    h=sha(path);(OUT/"casos_rotulados.sha256").write_text(f"{h}  casos_rotulados.csv\n",encoding="ascii")
    model,manifest=load_verified_model();guard=load_language_guard();df=evaluate(rows,model,manifest,guard);patterns,cal=calibrate(df);df=apply_correction(df,patterns);df.to_csv(OUT/"resultados_caso_a_caso.csv",index=False,encoding="utf-8-sig")
    current=summarize(df,"resultado_atual");oos_lang=summarize(df[df.group=="fora_do_escopo"],"resultado_atual",True);measure=df[(df.group=="fora_do_escopo")&(df.split_correcao=="medicao")];before=summarize(measure,"resultado_atual",True);corrected=summarize(measure,"resultado_correcao",True)
    for row in corrected: row["antes_direto_fila_errada"]=next(x["direto_fila_errada"] for x in before if x["idioma"]==row["idioma"])
    b1=base1(model,manifest,guard,patterns);cost=frozen_cost(model,manifest,guard,patterns)
    error_rows=automatic_error_by_group(df,"resultado_correcao")
    payload={"premissa":"sintéticos gerados por IA; evidência complementar","casos_sha256":h,"checagem_duplicidade":"normalizado sem pontuação/números: zero repetições","grupos_atuais":current,"erro_entre_encaminhados_por_grupo_antes":automatic_error_by_group(df,"resultado_atual"),"erro_entre_encaminhados_por_grupo_com_barreira":error_rows,"fora_escopo_por_idioma":oos_lang,"calibracao_correcao_fora_escopo":cal,"correcao_medicao_fora_escopo":corrected,"padroes_selecionados":patterns,"base1":b1,"custo_teste_congelado":cost}
    (OUT/"resumo.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8");(OUT/"relatorio.md").write_text(report(current,oos_lang,corrected,b1,cost,cal,h,patterns,error_rows),encoding="utf-8");print(json.dumps(payload,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
