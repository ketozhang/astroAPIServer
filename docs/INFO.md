---
title: AstroSQL
---

## Authentication for API Calls

There are two choices when implementing secure authentication for API calls:

1. **Session Cookies**
    Pros:
    * Natural to store authentication data in sessions
    * Logs out after removing cookie

    Cons:
    * Requires server-stored login status table
    * Sesson login token can be modified although randomize tokens are nonhuman-readable.

2. **JWT**

    Pros:
    * Session login tokens (called JWT tokens) is signed so modification attempts essentially useless.

    Cons:
    * Requires user-stored JWT token. The JWT token is either locally stored (subject to XSS attacks) or stored in session cookies (subject to CSRF attacks).

The choice for astroAPIServer is to use JWT stored via session cookies. To protect against CSRF attacks, astroAPIServer uses CSRF tokens.