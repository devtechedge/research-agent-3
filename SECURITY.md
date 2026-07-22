# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are supported:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of Chronic Lyme Research Agent seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do NOT report security vulnerabilities through public GitHub issues.**

### How to Report a Security Vulnerability?

If you think you have found a security vulnerability in our project, please send an email to: **[INSERT SECURITY EMAIL ADDRESS]**

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### What to Expect

- **Initial Response**: You should receive an acknowledgment within 48 hours
- **Status Updates**: We will provide status updates every 7 days
- **Resolution Timeline**: We aim to resolve critical issues within 30 days

### Disclosure Policy

Once a security issue is reported, we follow this disclosure process:

1. **Confirmation**: We confirm the vulnerability and determine its impact
2. **Fix Development**: A fix is developed and tested
3. **Release**: A patched version is released
4. **Disclosure**: After 30 days from the release, we publicly disclose the issue

### Security Best Practices for Users

To use Chronic Lyme Research Agent securely:

1. **Keep Updated**: Always use the latest version
2. **Environment Variables**: Store sensitive data (API keys, passwords) in environment variables, never in code
3. **Access Control**: Limit access to the `.env` file and database credentials
4. **Network Security**: Run the agent in a secure network environment
5. **Email Security**: Use app-specific passwords for email accounts, not main account passwords
6. **Database Security**: Use strong passwords and limit database user permissions

### Third-Party Dependencies

We regularly audit and update our dependencies. If you find a vulnerability in a dependency, please report it using the process above.

## Security Measures

Current security measures implemented in the project:

- ✅ Input validation on all external data
- ✅ Secure handling of API keys and credentials via environment variables
- ✅ HTTPS for all external API communications
- ✅ Parameterized database queries to prevent SQL injection
- ⚠️ Rate limiting for API calls (planned)
- ⚠️ Audit logging (planned)

Thank you for helping keep Chronic Lyme Research Agent and our users safe!
