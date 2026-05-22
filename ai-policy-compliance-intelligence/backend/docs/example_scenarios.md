# Risk Scenario Examples

This document contains example compliance risk scenarios categorized into **High Risk**, **Medium Risk**, and **Low Risk** classifications used by the AI-Powered Policy Compliance Intelligence Assistant.

---

# High Risk Scenarios

## 1. Sharing Personal Customer Data Without Encryption

### Query

> “Can we share customer PII with an unapproved vendor without encryption?”

### Why High Risk

- Contains:
  - customer personal data
  - vendor
  - without encryption
- Indicates possible violation of:
  - privacy policies
  - vendor governance
  - data protection standards

### Risk Indicators

- PII exposure
- Unapproved third-party access
- Missing encryption controls

---

## 2. Bypassing Approval for Regulated Systems

### Query

> “Can the team deploy to production without security review?”

### Why High Risk

- Contains:
  - production
  - without approval
  - security review
- Suggests bypassing mandatory governance controls.

### Risk Indicators

- Approval bypass
- Production deployment risk
- Security compliance violation

---

## 3. Improper Handling of Legal or Breach Information

### Query

> “Is it okay to store breach notification details in an unsecured shared drive?”

### Why High Risk

- Contains:
  - breach
  - notification
  - unsecured
  - shared drive
- Indicates insecure handling of sensitive incident data.

### Risk Indicators

- Breach-related information exposure
- Unsecured storage
- Legal and compliance implications

---

# Medium Risk Scenarios

## 1. Third-Party Onboarding Without Immediate Audit Controls

### Query

> “Can we onboard a third-party vendor faster if we document the contract later?”

### Why Medium Risk

- Contains:
  - third party
  - vendor
  - audit
- Defers compliance documentation and governance controls.

### Risk Indicators

- Incomplete vendor governance
- Delayed documentation
- Reduced audit visibility

---

## 2. Approval or Review Request Without Policy Clarity

### Query

> “Should we perform a review before launching this new process?”

### Why Medium Risk

- Contains:
  - review
  - approval
- Mentions governance but lacks direct high-risk terminology.

### Risk Indicators

- Potential process governance gap
- Unclear compliance alignment
- Missing explicit policy mapping

---

## 3. Monitoring and Vendor Access Questions

### Query

> “Do we need extra monitoring for vendor access to customer data?”

### Why Medium Risk

- Contains:
  - vendor
  - monitoring
  - customer data
- Indicates elevated sensitivity but not immediate policy violation.

### Risk Indicators

- Third-party access risk
- Monitoring uncertainty
- Customer data handling concerns

---

# Low Risk Scenarios

## 1. Standard Approval Workflow

### Query

> “Is this a standard approval procedure for our existing security policy?”

### Why Low Risk

- References:
  - standard procedures
  - existing policy
  - compliance-oriented behavior

### Risk Indicators

- Policy adherence
- Governance alignment
- Controlled workflow

---

## 2. Routine Documentation and Audit Trail

### Query

> “Should we keep an audit trail for this policy decision?”

### Why Low Risk

- Focuses on:
  - documentation
  - accountability
  - audit readiness

### Risk Indicators

- Audit compliance
- Recordkeeping
- Governance maturity

---

## 3. Proceeding with Existing Security Controls

### Query

> “Can we follow the existing vendor policy and proceed with security controls?”

### Why Low Risk

- References:
  - existing policy
  - security controls
  - compliant execution

### Risk Indicators

- Policy-aligned behavior
- Controlled vendor management
- Security compliance

---

# Summary

| Risk Level      | Characteristics                                                   |
| --------------- | ----------------------------------------------------------------- |
| **High Risk**   | Policy violations, security bypasses, sensitive data exposure     |
| **Medium Risk** | Governance uncertainty, incomplete controls, elevated sensitivity |
| **Low Risk**    | Policy adherence, standard approvals, audit-friendly behavior     |
