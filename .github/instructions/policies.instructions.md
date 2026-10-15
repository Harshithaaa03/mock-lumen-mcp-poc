# Policies Instructions

> **POC NOTICE:** The policies in this file are **sample documentation** for the
> `mock-lumen-mcp-poc` demonstration application. They are NOT approved corporate
> compliance guidance, legal advice, official security policy, or Lumen policy.
> Do not use this document as a basis for production security or compliance decisions.

## Access Control

### Authentication
**[POC ONLY – NOT IMPLEMENTED]**

The Todo List application does NOT implement authentication. Any client that can reach the
backend API can create, read, update, and delete any task. This is an intentional simplification
for the POC.

**Recommendation for production:** Implement OAuth 2.0 / OIDC (e.g., Azure AD / Entra ID)
before deploying beyond a private development environment.

### Authorization
**[POC ONLY – NOT IMPLEMENTED]**

No role-based access control (RBAC) or attribute-based access control (ABAC) is implemented.
All API endpoints are open to any caller.

**Recommendation for production:** Implement role separation (e.g., admin vs. read-only user)
before any real-world deployment.

### Assignee
**[IMPLEMENTED – DEMONSTRATION FEATURE]**

The `assignee` field accepts any free-text string. It does not validate against a user directory.
The POC documents this clearly and explicitly labels assignment as a demonstration feature.

---

## Data Handling

### Data Storage
- **[IMPLEMENTED]** Task data is stored in a SQLite file (`backend/todo.db`).
- The SQLite file is excluded from version control via `.gitignore`.
- **[PROPOSED – NOT IMPLEMENTED]** In production, replace SQLite with a managed relational
  database (e.g., PostgreSQL on Azure) with encrypted connections.

### Data in Transit
- **[POC ONLY]** Local development runs over plain HTTP.
- **[PROPOSED – NOT IMPLEMENTED]** Production deployments should enforce HTTPS with TLS 1.2+.

### Data at Rest Encryption
- **[NOT IMPLEMENTED]** SQLite data is stored unencrypted on disk.
- **[PROPOSED]** Use database-level encryption or OS-level disk encryption in production.

### Personal Data
- The `assignee` field may contain a person's name or username.
- No other personal data fields exist in the schema.
- **[PROPOSED]** A production version should include a data retention policy, a right-to-erasure
  mechanism, and a privacy notice if handling personal data under GDPR, CCPA, or similar.

---

## MCP Server Policies

### POC Scope
- The Mock Lumen MCP server is clearly labeled as a POC in all responses.
- It does not represent or claim to be the official Lumen service.
- It does not access any production Lumen systems.

### Information Exposure
- **[IMPLEMENTED]** The MCP server reads only `.github/instructions/*.md` files.
- **[IMPLEMENTED]** The MCP server does not expose environment variables, secrets, or internal
  filesystem paths beyond the relative paths documented in context files.
- **[IMPLEMENTED]** No API keys, tokens, or credentials are included in context files or MCP responses.

### Authentication for MCP Endpoint
- **[NOT IMPLEMENTED IN POC]** The MCP server has no request-level authentication.
- **[PROPOSED]** Before public deployment, add bearer token or API key verification.
- If connected to Microsoft Copilot Studio, use the authentication mechanism supported by
  the Copilot Studio MCP connection flow (refer to the README for current guidance).

---

## Security Recommendations (Not Implemented in POC)

The following are sample recommendations for a production version of this application.
None of these controls are currently implemented:

1. Rate limiting on the backend API
2. Input sanitization beyond Pydantic validation
3. Audit logging of data modifications
4. Secrets management (e.g., Azure Key Vault)
5. Dependency scanning and SCA in CI/CD
6. Container image vulnerability scanning
7. Network-level access controls (VNet, firewall rules)
