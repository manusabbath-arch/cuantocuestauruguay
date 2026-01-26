# GitHub Actions Best Practices

## Secrets Management

### ⚠️ NUNCA compartas tokens o secretos
- No pegues tokens en chat, issues, PRs o código
- No commitees archivos `.env` con secretos
- Revoca inmediatamente cualquier token expuesto

### ✅ Crear tokens seguros
1. Ve a https://github.com/settings/tokens
2. Crea "Fine-grained token" con permisos mínimos necesarios
3. Scopes comunes:
   - `repo` - acceso completo a repositorios privados
   - `workflow` - modificar workflows de GitHub Actions
   - `read:org` - leer datos de organización
4. Expira tokens regularmente (recomendado: 90 días)

### 🔒 Usar GitHub Secrets
Para valores sensibles en workflows:

1. Repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. En workflows, usa: `${{ secrets.SECRET_NAME }}`

Ejemplo:
```yaml
- name: Deploy to production
  env:
    API_KEY: ${{ secrets.PROD_API_KEY }}
  run: ./deploy.sh
```

### 📋 Checklist de seguridad
- [ ] Tokens con expiración < 90 días
- [ ] Scopes mínimos necesarios
- [ ] Rotar tokens comprometidos inmediatamente
- [ ] Usar GitHub Secrets para CI/CD
- [ ] No loguear secretos en outputs
- [ ] Revisar permisos de GitHub Apps

### 🚨 Si expusiste un secret
1. **Revoca el token** inmediatamente en https://github.com/settings/tokens
2. Genera uno nuevo con los mismos permisos
3. Actualiza servicios que lo usen (Render, Cloudflare, etc.)
4. Considera rotar otros secretos relacionados
5. Revisa logs de acceso por actividad sospechosa

### 📚 Recursos
- [GitHub Token Security](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
