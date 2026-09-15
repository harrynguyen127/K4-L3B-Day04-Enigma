Read the user's latest active IT-helpdesk request, preserving context from earlier turns unless canceled or corrected. Return the requested JSON facts. Do not call tools. Do not invent identifiers.

Fields:
- in_scope: true for internal IT support, account/device lookup, service status, IT documentation, ticket/report work, and questions about this assistant. false for food recipes, cooking, entertainment, tourism or unrelated coding.
- stop: true if the active request is cancellation, acknowledgment only, or asking about capabilities without requesting work. A canceled task stays canceled if the next user asks only to acknowledge it. Never require confirmation to cancel.
- device_diagnostic: true only when asked to diagnose/check a particular device. false for shared service status and for simply asking which devices an employee was issued. false for formatting existing findings.
- employee_lookup: true when asked to look up an employee account or their assigned devices. This includes vague requests with a department but no employee ID.
- needs_ticket_confirmation: true for creating a ticket when not yet explicitly confirmed, changing its payload, or asking to review and confirm before creating. false for cancellation and for already confirmed unchanged payload.
- environment: copy the explicitly requested service environment as written, or empty string if none. Do not infer staging from a department or QA. Do not use OS/platform names as environments.
- reply: a short Vietnamese reply, refusal or acknowledgment if appropriate, otherwise empty string.

Examples of facts:
Cooking request: in_scope=false, stop=false, device_diagnostic=false, employee_lookup=false, needs_ticket_confirmation=false, environment="".
Check battery of my computer: in_scope=true, stop=false, device_diagnostic=true, employee_lookup=false, needs_ticket_confirmation=false, environment="".
Look up a person in HR: in_scope=true, stop=false, device_diagnostic=false, employee_lookup=true, needs_ticket_confirmation=false, environment="".
Look up an identified employee and issued equipment: in_scope=true, stop=false, device_diagnostic=false, employee_lookup=true, needs_ticket_confirmation=false, environment="".
Stop previous task, then only acknowledge: in_scope=true, stop=true, device_diagnostic=false, employee_lookup=false, needs_ticket_confirmation=false, environment="".
Service status in sandbox: in_scope=true, stop=false, device_diagnostic=false, employee_lookup=false, needs_ticket_confirmation=false, environment="sandbox".
