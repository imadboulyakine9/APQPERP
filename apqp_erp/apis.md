Base URL: Assume all APIs are prefixed with /api/v1/.

Authentication: All endpoints (unless specified otherwise) require the user to be authenticated. Tokens (like JWT or DRF's TokenAuthentication) are common.

Permissions: Specific permissions (e.g., being a "Manager", having specific ProjectPermission) will gate access to certain endpoints or actions. We'll note these.

Serialization: Input/Output JSON will generally mirror the Django model fields, but serializers can customize this (e.g., nesting related objects).

Standard Responses:

200 OK: Successful GET, PUT, PATCH. Response body contains data.

201 Created: Successful POST. Response body contains the created resource.

204 No Content: Successful DELETE. No response body.

400 Bad Request: Invalid input data (validation errors). Response body contains error details.

401 Unauthorized: Authentication missing or invalid.

403 Forbidden: Authenticated user lacks permission for the action.

404 Not Found: Resource doesn't exist.

API Blueprint (MVP)
Authentication

(These are standard patterns, implementation depends on chosen library)

Login

Endpoint: POST /api/v1/auth/login/

Description: Authenticate user and receive a token.

Permissions: Public.

Input Body: { "email": "user@example.com", "password": "..." }

Output (200 OK): { "access_token": "...", "refresh_token": "..." } (or similar based on auth type)

Output (400/401): Error details.

Refresh Token

Endpoint: POST /api/v1/auth/refresh/

Input Body: { "refresh_token": "..." }

Output (200 OK): { "access_token": "..." }

Users

(Focus on current user and listing for selection)

Get Current User Info

Endpoint: GET /api/v1/users/me/

Description: Retrieve details for the currently logged-in user.

Permissions: Authenticated User.

Input: None (Auth Token in header).

Output (200 OK): { "user_id": "...", "name": "...", "email": "...", "department_name": "...", "role": "..." }

List Users (for selection)

Endpoint: GET /api/v1/users/

Description: Get a list of users, potentially filtered (e.g., by name/email for adding to teams/projects ).

Permissions: Authenticated User (managers).

Input Query Params: ?search=John (optional filtering)

Output (200 OK): [ { "user_id": "...", "name": "...", "email": "..." }, ... ] (Simplified list view)

Teams

Create Team

Endpoint: POST /api/v1/teams/

Description: Create a new team.

Permissions: Authenticated User (maybe restrict to Managers/Admins).

Input Body: { "name": "New Team Name", "member_ids": ["user_uuid_1", "user_uuid_2"] } (optional initial members)

Output (201 Created): { "team_id": "...", "name": "...", "members": [...] } (serialized members)

List Teams

Endpoint: GET /api/v1/teams/

Description: Get a list of teams.

Permissions: Authenticated User.

Output (200 OK): [ { "team_id": "...", "name": "...", "member_count": 5 }, ... ] (Simplified list view)

Get Team Details

Endpoint: GET /api/v1/teams/{team_id}/

Description: Retrieve details for a specific team, including members.

Permissions: Authenticated User.

Output (200 OK): { "team_id": "...", "name": "...", "members": [ { "user_id": "...", "name": "...", "email": "..." }, ... ] }

Update Team

Endpoint: PATCH /api/v1/teams/{team_id}/

Description: Update team details (e.g., name).

Permissions: Team manager/Admin (requires permission logic).

Input Body: { "name": "Updated Team Name" }

Output (200 OK): Updated team details.

Manage Team Members

Add Member: POST /api/v1/teams/{team_id}/members/

Input Body: { "user_id": "user_uuid_to_add" }

Permissions: Team manager/Admin.

Output (200 OK / 201 Created): Confirmation or updated member list.

Remove Member: DELETE /api/v1/teams/{team_id}/members/{user_id}/

Permissions: Team manager/Admin.

Output (204 No Content): Success.

Clients

Create Client

Endpoint: POST /api/v1/clients/

Description: Create a new client record.

Permissions: Authenticated User (maybe Managers/Sales roles).

Input Body: { "name": "Client A", "email": "contact@clienta.com" }

Output (201 Created): { "client_id": "...", "name": "...", "email": "..." }

List Clients

Endpoint: GET /api/v1/clients/

Description: Get a list of all clients.

Permissions: Authenticated User.

Input Query Params: ?search=Client (optional)

Output (200 OK): [ { "client_id": "...", "name": "...", "email": "..." }, ... ]

Get Client Details

Endpoint: GET /api/v1/clients/{client_id}/

Permissions: Authenticated User.

Output (200 OK): { "client_id": "...", "name": "...", "email": "..." } (Potentially list linked projects here too)

Update Client

Endpoint: PATCH /api/v1/clients/{client_id}/

Permissions: Authenticated User (maybe Managers/Sales roles).

Input Body: { "name": "...", "email": "..." }

Output (200 OK): Updated client details.

Delete Client

Endpoint: DELETE /api/v1/clients/{client_id}/

Permissions: Admin/Manager roles.

Output (204 No Content): Success.

Projects

Create Project

Endpoint: POST /api/v1/projects/

Description: Create a new project.

Permissions: Requires 'Manager' role (or specific permission). Backend needs to verify request.user.role == 'Manager' or similar logic.

Input Body: { "name": "Project Alpha", "desc": "...", "status": "Planning", "responsible_user_id": "user_uuid", "team_id": "team_uuid", "client_ids": ["client_uuid_1"] }

Output (201 Created): Serialized Project object.

List Projects

Endpoint: GET /api/v1/projects/

Description: Get a list of projects the user has access to (based on team membership, responsibility, or ProjectPermission).

Permissions: Authenticated User. Backend filters based on user's access.

Input Query Params: ?status=Active, ?responsible_user_id=..., ?team_id=... (optional filtering)

Output (200 OK): [ { "project_id": "...", "name": "...", "status": "...", "responsible_user": { "user_id": "...", "name": "..." }, "team": { "team_id": "...", "name": "..." } }, ... ] (Simplified list view)

Get Project Details

Endpoint: GET /api/v1/projects/{project_id}/

Description: Retrieve full details for a specific project.

Permissions: User must have access to the project.

Output (200 OK): { "project_id": "...", "name": "...", ..., "team": {...}, "clients": [...], "phases": [...], "permissions": [...] } (More detailed, potentially nested related objects)

Update Project

Endpoint: PATCH /api/v1/projects/{project_id}/

Description: Partially update project details.

Permissions: User needs 'Edit' or higher permission on the project.

Input Body: { "status": "Active", "desc": "Updated description", "client_ids": ["client_uuid_1", "client_uuid_2"] } (Can update specific fields, including client links)

Output (200 OK): Updated project object.

Delete Project

Endpoint: DELETE /api/v1/projects/{project_id}/

Description: Delete a project.

Permissions: User needs 'Admin' permission on the project (or global Admin role).

Output (204 No Content): Success.

Project Permissions

List Project Permissions

Endpoint: GET /api/v1/projects/{project_id}/permissions/

Description: List users and their permission levels for a specific project.

Permissions: User needs 'Manage' or 'Admin' permission on the project.

Output (200 OK): [ { "user": { "user_id": "...", "name": "..." }, "permission_level": "Edit" }, ... ]

Set/Update User Permission

Endpoint: PUT /api/v1/projects/{project_id}/permissions/{user_id}/

Description: Set or update the permission level for a specific user on this project. Use PUT to ensure the state is fully set.

Permissions: User needs 'Manage' or 'Admin' permission on the project.

Input Body: { "permission_level": "Read" } (Use one of the PROJECT_PERMISSION_LEVEL_CHOICES)

Output (200 OK): { "user": {...}, "permission_level": "Read" }

Revoke User Permission

Endpoint: DELETE /api/v1/projects/{project_id}/permissions/{user_id}/

Description: Remove a user's specific permission entry for this project.

Permissions: User needs 'Manage' or 'Admin' permission on the project.

Output (204 No Content): Success.

Phases (Nested under Projects)

List Phases for Project

Endpoint: GET /api/v1/projects/{project_id}/phases/

Description: Get the list of phases for a specific project.

Permissions: User needs 'Read' access to the project.

Output (200 OK): [ { "phase_id": "...", "level": 1, "status": "...", "tasks_count": 3 }, ... ] (List view)

Create Phase

Endpoint: POST /api/v1/projects/{project_id}/phases/

Description: Create a new phase for the project. Backend logic might auto-assign level or use a template.

Permissions: User needs 'Edit' permission on the project.

Input Body: { "level": 1, "status": "Pending", "configuration": {...}, "documents": [...], "template_id": "..." } (Template ID might trigger configuration/task creation)

Output (201 Created): Serialized Phase object.

Get Phase Details

Endpoint: GET /api/v1/projects/{project_id}/phases/{phase_id}/

Description: Get full details of a specific phase, potentially including its tasks.

Permissions: User needs 'Read' access to the project.

Output (200 OK): { "phase_id": "...", "level": ..., "status": ..., "configuration": ..., "documents": ..., "tasks": [...] }

Update Phase

Endpoint: PATCH /api/v1/projects/{project_id}/phases/{phase_id}/

Description: Update phase details (e.g., status, documents).

Permissions: User needs 'Edit' permission on the project.

Input Body: { "status": "InProgress", "documents": [...] }

Output (200 OK): Updated Phase object.

Delete Phase

Endpoint: DELETE /api/v1/projects/{project_id}/phases/{phase_id}/

Description: Delete a phase.

Permissions: User needs 'Admin' permission on the project.

Output (204 No Content): Success.

Tasks (Nested under Phases)

List Tasks for Phase

Endpoint: GET /api/v1/projects/{project_id}/phases/{phase_id}/tasks/

Permissions: User needs 'Read' access to the project.

Output (200 OK): [ { "task_id": "...", "name": "...", "status": "...", "assigned_user": { "user_id": "...", "name": "..." } }, ... ]

Create Task

Endpoint: POST /api/v1/projects/{project_id}/phases/{phase_id}/tasks/

Permissions: User needs 'Edit' access to the project.

Input Body: { "name": "Task Name", "description": "...", "status": "Pending", "assigned_user_id": "user_uuid", "due_date": "YYYY-MM-DD" }

Output (201 Created): Serialized Task object.

Get Task Details

Endpoint: GET /api/v1/projects/{project_id}/phases/{phase_id}/tasks/{task_id}/

Permissions: User needs 'Read' access to the project.

Output (200 OK): Full Task object details.

Update Task

Endpoint: PATCH /api/v1/projects/{project_id}/phases/{phase_id}/tasks/{task_id}/

Permissions: User needs 'Edit' access to the project (or maybe just the assigned user can update status?). Define this rule.

Input Body: { "status": "Completed", "assigned_user_id": "...", "description": "..." }

Output (200 OK): Updated Task object.

Delete Task

Endpoint: DELETE /api/v1/projects/{project_id}/phases/{phase_id}/tasks/{task_id}/

Permissions: User needs 'Edit'/'Admin' access to the project.

Output (204 No Content): Success.

Get My Tasks

Endpoint: GET /api/v1/users/me/tasks/

Description: Get a list of tasks assigned to the currently logged-in user across all projects.

Permissions: Authenticated User.

Input Query Params: ?status=Pending, ?status=InProgress (optional filtering)

Output (200 OK): [ { "task_id": "...", "name": "...", "status": "...", "project": {"project_id": "...", "name": "..."}, "phase": {"phase_id": "...", "level": ...} }, ... ]

Phase Templates (Read-Only for MVP)

List Phase Templates

Endpoint: GET /api/v1/phase-templates/

Permissions: Authenticated User.

Output (200 OK): [ { "template_id": "...", "name": "...", "applicable_level": ... }, ... ]

Get Phase Template Details

Endpoint: GET /api/v1/phase-templates/{template_id}/

Permissions: Authenticated User.

Output (200 OK): { "template_id": "...", "name": "...", "content": {...}, "applicable_level": ... }

History Logs (Read-Only)

List History Logs (Filtered)

Endpoint: GET /api/v1/history-logs/

Description: Get recent activity logs, requires filtering (e.g., by project).

Permissions: Authenticated User.

Input Query Params: ?project_id=..., ?phase_id=..., ?task_id=..., ?user_id=... (Backend enforces user can only see logs for projects they have access to). Requires pagination.

Output (200 OK): Paginated list: { "count": ..., "next": "...", "previous": "...", "results": [ { "log_id": "...", "timestamp": "...", "name": "...", "status": "...", "user": {...}, "project": {...}, "phase": {...}, "task": {...}, "details": {...} }, ... ] }

This blueprint provides a solid starting point for your MVP API. Remember that implementing permissions correctly is crucial and will require careful design in your DRF views/viewsets.