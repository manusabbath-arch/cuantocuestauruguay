# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of PreciosRegulados.uy seriously. If you discover a security vulnerability, please follow these steps:

### 🔒 Private Disclosure

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please report security issues privately:

1. **Email:** Send details to [SECURITY CONTACT - ADD YOUR EMAIL]
2. **GitHub Security Advisories:** Use the [Private Vulnerability Reporting](https://github.com/manusabbath-arch/cuantocuestauruguay/security/advisories/new) feature

### 📋 What to Include

Please provide:
- Type of vulnerability (XSS, SQL injection, CSRF, etc.)
- Steps to reproduce the issue
- Affected component (backend API, frontend, database, etc.)
- Potential impact
- Any suggested fixes (optional)

### ⏱️ Response Timeline

- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Depends on severity
  - Critical: 24-48 hours
  - High: 7 days
  - Medium: 30 days
  - Low: 90 days

### 🎖️ Recognition

We maintain a [Security Hall of Fame](https://cuantocuestauruguay.com/security-thanks) to recognize responsible disclosure. With your permission, we'll credit you for your findings.

## Security Measures

### Current Protections

- ✅ HTTPS/TLS encryption (Cloudflare SSL)
- ✅ CORS restrictions
- ✅ Input validation (Pydantic)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Rate limiting (Cloudflare)
- ✅ Dependency scanning (Dependabot)

### Planned Enhancements

See [ROADMAP.md](../ROADMAP.md) for security improvements:
- WAF (Web Application Firewall)
- Security headers (CSP, HSTS)
- API authentication with keys
- Advanced rate limiting
- Monitoring and alerting (Sentry)

## Scope

### In Scope

- Backend API (FastAPI)
- Frontend application (React)
- Database (PostgreSQL)
- Infrastructure (Render.com, Cloudflare)
- Authentication/Authorization mechanisms
- Data validation and sanitization

### Out of Scope

- Social engineering attacks
- Physical security
- Third-party services (CKAN API, government data sources)
- DDoS attacks (handled by Cloudflare)

## Best Practices for Contributors

When contributing code:

1. **Never commit secrets**
   - Use `.env` files (git-ignored)
   - Use environment variables
   - Scan with `git-secrets` or `trufflehog`

2. **Validate all inputs**
   - Use Pydantic models
   - Sanitize user input
   - Check bounds and types

3. **Follow OWASP guidelines**
   - [OWASP Top 10](https://owasp.org/www-project-top-ten/)
   - [OWASP API Security](https://owasp.org/www-project-api-security/)

4. **Keep dependencies updated**
   - Review Dependabot PRs
   - Run `npm audit` and `safety check`

5. **Write tests**
   - Include security test cases
   - Test authentication/authorization
   - Validate error handling

## Contact

For non-security issues, use [GitHub Issues](https://github.com/manusabbath-arch/cuantocuestauruguay/issues).

For security concerns: [ADD YOUR SECURITY EMAIL]

---

Last updated: January 26, 2026
