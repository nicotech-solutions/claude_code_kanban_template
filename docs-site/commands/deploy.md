# /deploy

Deploy para produção com checklist completo de segurança.

---

## Quando usar

- Para fazer deploy de uma release para produção
- Após aprovação do TL e do PO

---

## Checklist de deploy

**Antes:**
- [ ] Todos os testes passando em CI
- [ ] Variáveis de ambiente configuradas no ambiente de destino
- [ ] Secrets no secret manager — nunca em código ou CI logs
- [ ] Rollback definido (versão anterior disponível)
- [ ] Health check configurado

**Durante:**
- [ ] Deploy gradual (blue/green ou canary) quando possível
- [ ] Monitorar métricas-chave nos primeiros 15 minutos

**Após:**
- [ ] Smoke test em produção
- [ ] Alertas verificados (não silenciados)
- [ ] Documentar qualquer configuração manual

---

## O que faz

1. **infra-devops executa o checklist** completo acima
2. Dispara o pipeline de deploy configurado
3. Monitora logs e métricas por 15 minutos
4. Reporta resultado (sucesso / falha / rollback necessário)
