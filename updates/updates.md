# Decisões Técnicas

## Docker Compose — Volume Persistente do Metabase

**Data:** 12/04/2026
**Motivo:** O Metabase perdia todos os dashboards ao recriar os containers.

**Solução aplicada:**
Adicionado volume persistente `metabase_data` no `docker-compose.yml`:

```yaml
volumes:
  - metabase_data:/metabase-data
environment:
  MB_DB_TYPE: h2
  MB_DB_FILE: /metabase-data/metabase.db
```

**Resultado:**
Dashboards, conexões e usuário do Metabase agora persistem entre reinicializações dos containers.

**Atenção:**
Por conta de compatibilidade, foi necessário substituir um novo arquivo docker-compose, mas o histórico ainda está preservado.