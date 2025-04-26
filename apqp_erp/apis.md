Okay, let's refine the database schema for documents and add the requested API endpoints.

1. Database Schema Modification (Conceptual)

We need a dedicated Document model instead of just a JSON field on Phase.

New Model:

# models.py (Conceptual addition/change)

class Document(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE, # Delete document if phase is deleted
        related_name='phase_documents'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Keep document if user is deleted
        related_name='uploaded_documents',
        null=True
    )
    # Requires configuring MEDIA_ROOT and MEDIA_URL in settings.py
    file = models.FileField(upload_to='project_documents/%Y/%m/%d/')
    name = models.CharField(max_length=255, blank=True, help_text="Original filename or custom name")
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically set the name from the filename if not provided
        if not self.name and self.file:
            self.name = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (Phase: {self.phase.level} - {self.phase.project.name})"

    class Meta:
        ordering = ['-uploaded_at']


Modification to Phase model:

Remove: documents = models.JSONField(...)

Now, a Phase can have multiple Document objects linked to it via the ForeignKey.

2. Updated API Blueprint (Markdown Format)
# API Blueprint (MVP - Revision 2)

**Base URL:** `/api/v1/`

**Authentication:** Required for most endpoints (e.g., JWT Token in `Authorization: Bearer <token>` header).

**Standard Responses:**
*   `200 OK`: Success (GET, PUT, PATCH) - Body: Data
*   `201 Created`: Success (POST) - Body: Created resource data
*   `204 No Content`: Success (DELETE) - Body: None
*   `400 Bad Request`: Invalid input/Validation error - Body: Error details
*   `401 Unauthorized`: Authentication failed/missing
*   `403 Forbidden`: User authenticated but lacks permission
*   `404 Not Found`: Resource not found

---

## Authentication

### 1. Login
*   **Endpoint:** `POST /auth/login/`
*   **Description:** Authenticate user, receive tokens.
*   **Permissions:** Public.
*   **Input Body:** `{ "email": "...", "password": "..." }`
*   **Output (200 OK):** `{ "access_token": "...", "refresh_token": "..." }`

### 2. Refresh Token
*   **Endpoint:** `POST /auth/refresh/`
*   **Description:** Obtain a new access token using a refresh token.
*   **Permissions:** Public (requires valid refresh token).
*   **Input Body:** `{ "refresh_token": "..." }`
*   **Output (200 OK):** `{ "access_token": "..." }`

---

## Users

### 1. Get Current User Info
*   **Endpoint:** `GET /users/me/`
*   **Description:** Retrieve details for the currently logged-in user.
*   **Permissions:** Authenticated User.
*   **Output (200 OK):** `{ "user_id": "...", "name": "...", "email": "...", "department_name": "...", "role": "..." }`

### 2. List Users (for selection)
*   **Endpoint:** `GET /users/`
*   **Description:** Get a list of users (e.g., for assigning tasks, permissions).
*   **Permissions:** Authenticated User.
*   **Query Params:** `?search=John` (optional filtering)
*   **Output (200 OK):** `[ { "user_id": "...", "name": "...", "email": "..." }, ... ]`

### 3. Get User's Assigned Tasks
*   **Endpoint:** `GET /users/me/tasks/`
*   **Description:** Get a list of tasks assigned to the currently logged-in user across all projects.
*   **Permissions:** Authenticated User.
*   **Query Params:** `?status=Pending`, `?status=InProgress` (optional filtering by task status)
*   **Output (200 OK):** `[ { "task_id": "...", "name": "...", "status": "...", "project": {"project_id": "...", "name": "..."}, "phase": {"phase_id": "...", "level": ...}, "due_date": "YYYY-MM-DD" }, ... ]`

---

## Teams

### 1. Create Team
*   **Endpoint:** `POST /teams/`
*   **Permissions:** Authenticated User (potentially restricted, e.g., Managers).
*   **Input Body:** `{ "name": "...", "member_ids": ["uuid1", "uuid2"] }`
*   **Output (201 Created):** `{ "team_id": "...", "name": "...", "members": [...] }`

### 2. List Teams
*   **Endpoint:** `GET /teams/`
*   **Permissions:** Authenticated User.
*   **Output (200 OK):** `[ { "team_id": "...", "name": "...", "member_count": ... }, ... ]`

### 3. Get Team Details
*   **Endpoint:** `GET /teams/{team_id}/`
*   **Permissions:** Authenticated User.
*   **Output (200 OK):** `{ "team_id": "...", "name": "...", "members": [...] }`

### 4. Update Team
*   **Endpoint:** `PATCH /teams/{team_id}/`
*   **Permissions:** Team Manager/Admin.
*   **Input Body:** `{ "name": "..." }`
*   **Output (200 OK):** Updated team object.

### 5. Add Team Member
*   **Endpoint:** `POST /teams/{team_id}/members/`
*   **Permissions:** Team Manager/Admin.
*   **Input Body:** `{ "user_id": "..." }`
*   **Output (200 OK/201 Created):** Success confirmation or updated member list.

### 6. Remove Team Member
*   **Endpoint:** `DELETE /teams/{team_id}/members/{user_id}/`
*   **Permissions:** Team Manager/Admin.
*   **Output (204 No Content):** Success.

---

## Clients

### 1. Create Client
*   **Endpoint:** `POST /clients/`
*   **Permissions:** Authenticated User (e.g., Managers/Sales).
*   **Input Body:** `{ "name": "...", "email": "..." }`
*   **Output (201 Created):** `{ "client_id": "...", "name": "...", "email": "..." }`

### 2. List Clients
*   **Endpoint:** `GET /clients/`
*   **Permissions:** Authenticated User.
*   **Query Params:** `?search=...` (optional)
*   **Output (200 OK):** `[ { "client_id": "...", "name": "...", "email": "..." }, ... ]`

### 3. Get Client Details
*   **Endpoint:** `GET /clients/{client_id}/`
*   **Permissions:** Authenticated User.
*   **Output (200 OK):** `{ "client_id": "...", "name": "...", "email": "..." }`

### 4. Update Client
*   **Endpoint:** `PATCH /clients/{client_id}/`
*   **Permissions:** Authenticated User (e.g., Managers/Sales).
*   **Input Body:** `{ "name": "...", "email": "..." }`
*   **Output (200 OK):** Updated client object.

### 5. Delete Client
*   **Endpoint:** `DELETE /clients/{client_id}/`
*   **Permissions:** Admin/Manager.
*   **Output (204 No Content):** Success.

---

## Projects

### 1. Create Project
*   **Endpoint:** `POST /projects/`
*   **Permissions:** 'Manager' role or equivalent permission required.
*   **Input Body:** `{ "name": "...", "desc": "...", "status": "...", "responsible_user_id": "...", "team_id": "...", "client_ids": [...] }`
*   **Output (201 Created):** Serialized Project object.

### 2. List Projects
*   **Endpoint:** `GET /projects/`
*   **Permissions:** Authenticated User (filtered based on user's access).
*   **Query Params:** `?status=...`, `?responsible_user_id=...`, `?team_id=...` (optional)
*   **Output (200 OK):** `[ { "project_id": "...", "name": "...", "status": "...", "responsible_user": {...}, "team": {...} }, ... ]`

### 3. Get Project Details
*   **Endpoint:** `GET /projects/{project_id}/`
*   **Permissions:** User needs access to the project.
*   **Output (200 OK):** `{ "project_id": "...", "name": "...", ..., "team": {...}, "clients": [...], "phases": [...], "permissions": [...] }`

### 4. Update Project
*   **Endpoint:** `PATCH /projects/{project_id}/`
*   **Permissions:** User needs 'Edit' or higher permission on the project.
*   **Input Body:** `{ "status": "...", "desc": "...", "client_ids": [...] }`
*   **Output (200 OK):** Updated project object.

### 5. Delete Project
*   **Endpoint:** `DELETE /projects/{project_id}/`
*   **Permissions:** User needs 'Admin' permission on the project.
*   **Output (204 No Content):** Success.

---

## Project Permissions (Nested under Projects)

### 1. List Project Permissions
*   **Endpoint:** `GET /projects/{project_id}/permissions/`
*   **Permissions:** User needs 'Manage' or 'Admin' permission on the project.
*   **Output (200 OK):** `[ { "user": { "user_id": "...", "name": "..." }, "permission_level": "..." }, ... ]`

### 2. Set/Update User Permission
*   **Endpoint:** `PUT /projects/{project_id}/permissions/{user_id}/`
*   **Permissions:** User needs 'Manage' or 'Admin' permission on the project.
*   **Input Body:** `{ "permission_level": "Read | Edit | Manage | Admin" }`
*   **Output (200 OK):** `{ "user": {...}, "permission_level": "..." }`

### 3. Revoke User Permission
*   **Endpoint:** `DELETE /projects/{project_id}/permissions/{user_id}/`
*   **Permissions:** User needs 'Manage' or 'Admin' permission on the project.
*   **Output (204 No Content):** Success.

---

## Phases (Nested under Projects)

### 1. List Phases for Project
*   **Endpoint:** `GET /projects/{project_id}/phases/`
*   **Permissions:** User needs 'Read' access to the project.
*   **Output (200 OK):** `[ { "phase_id": "...", "level": ..., "status": "...", "tasks_count": ..., "documents_count": ... }, ... ]`

### 2. Create Phase
*   **Endpoint:** `POST /projects/{project_id}/phases/`
*   **Permissions:** User needs 'Edit' permission on the project.
*   **Input Body:** `{ "level": ..., "status": "...", "configuration": {...}, "template_id": "..." (optional) }`
*   **Output (201 Created):** Serialized Phase object.

### 3. Get Phase Details
*   **Endpoint:** `GET /projects/{project_id}/phases/{phase_id}/`
*   **Permissions:** User needs 'Read' access to the project.
*   **Output (200 OK):** `{ "phase_id": "...", "level": ..., "status": ..., "configuration": ..., "phase_documents": [...], "tasks": [...] }` (Note: phase_documents replaces old documents field)

### 4. Update Phase
*   **Endpoint:** `PATCH /projects/{project_id}/phases/{phase_id}/`
*   **Permissions:** User needs 'Edit' permission on the project.
*   **Input Body:** `{ "status": "...", "configuration": {...} }`
*   **Output (200 OK):** Updated Phase object.

### 5. Delete Phase
*   **Endpoint:** `DELETE /projects/{project_id}/phases/{phase_id}/`
*   **Permissions:** User needs 'Admin' permission on the project.
*   **Output (204 No Content):** Success.

---

## Documents (Nested under Phases)

### 1. Upload Document to Phase
*   **Endpoint:** `POST /projects/{project_id}/phases/{phase_id}/documents/`
*   **Description:** Upload a file associated with a specific phase. Uses `multipart/form-data`.
*   **Permissions:** User needs 'Edit' permission on the project.
*   **Input (`form-data`):**
    *   `file`: The actual file being uploaded.
    *   `description`: (Optional) Text description of the file.
*   **Output (201 Created):** `{ "document_id": "...", "name": "...", "description": "...", "file_url": "/media/...", "uploaded_by": {...}, "uploaded_at": "..." }`

### 2. List Documents for Phase
*   **Endpoint:** `GET /projects/{project_id}/phases/{phase_id}/documents/`
*   **Description:** Get a list of documents associated with a specific phase.
*   **Permissions:** User needs 'Read' access to the project.
*   **Output (200 OK):** `[ { "document_id": "...", "name": "...", "description": "...", "file_url": "...", "uploaded_by": {...}, "uploaded_at": "..." }, ... ]`

### 3. Get Document Details / Download Info
*   **Endpoint:** `GET /documents/{document_id}/`
*   **Description:** Retrieve details for a specific document, including its download URL. *(Direct download might be handled separately or via the `file_url`)*.
*   **Permissions:** User needs 'Read' access to the project the document belongs to.
*   **Output (200 OK):** `{ "document_id": "...", "name": "...", "description": "...", "file_url": "...", "phase": {...}, "uploaded_by": {...}, "uploaded_at": "..." }`

### 4. Delete Document
*   **Endpoint:** `DELETE /documents/{document_id}/`
*   **Description:** Delete a specific document. The actual file on the server should also be removed.
*   **Permissions:** User needs 'Edit' or higher permission on the project the document belongs to (or be the uploader, depending on rules).
*   **Output (204 No Content):** Success.

---

## Tasks (Nested under Phases)

### 1. List Tasks for Phase
*   **Endpoint:** `GET /projects/{project_id}/phases/{phase_id}/tasks/`
*   **Permissions:** User needs 'Read' access to the project.
*   **Output (200 OK):** `[ { "task_id": "...", "name": "...", "status": "...", "assigned_user": {...} }, ... ]`

### 2. Create Task
*   **Endpoint:** `POST /projects/{project_id}/phases/{phase_id}/tasks/`
*   **Permissions:** User needs 'Edit' access to the project.
*   **Input Body:** `{ "name": "...", "description": "...", "status": "...", "assigned_user_id": "...", "due_date": "YYYY-MM-DD" }`
*   **Output (201 Created):** Serialized Task object.

### 3. Get Task Details
*   **Endpoint:** `GET /projects/{project_id}/phases/{phase_id}/tasks/{task_id}/`
*   **Permissions:** User needs 'Read' access to the project.
*   **Output (200 OK):** Full Task object details.

### 4. Update Task
*   **Endpoint:** `PATCH /projects/{project_id}/phases/{phase_id}/tasks/{task_id}/`
*   **Permissions:** User needs 'Edit' access to the project OR be the `assigned_user`.
*   **Input Body:** `{ "status": "...", "assigned_user_id": "...", "description": "..." }`
*   **Output (200 OK):** Updated Task object.

### 5. Delete Task
*   **Endpoint:** `DELETE /projects/{project_id}/phases/{phase_id}/tasks/{task_id}/`
*   **Permissions:** User needs 'Edit'/'Admin' access to the project.
*   **Output (204 No Content):** Success.

---

## Phase Templates (Read-Only)

### 1. List Phase Templates
*   **Endpoint:** `GET /phase-templates/`
*   **Permissions:** Authenticated User.
*   **Output (200 OK):** `[ { "template_id": "...", "name": "...", "applicable_level": ... }, ... ]`

### 2. Get Phase Template Details
*   **Endpoint:** `GET /phase-templates/{template_id}/`
*   **Permissions:** Authenticated User.
*   **Output (200 OK):** `{ "template_id": "...", "name": "...", "content": {...}, "applicable_level": ... }`

---

## History Logs (Read-Only)

### 1. List History Logs (Filtered)
*   **Endpoint:** `GET /history-logs/`
*   **Permissions:** Authenticated User (Backend filters by project access).
*   **Query Params:** `project_id=...` (Required recommended), `phase_id=...`, `task_id=...`, `user_id=...`, `page=...` (Pagination needed).
*   **Output (200 OK):** Paginated list: `{ "count": ..., "next": "...", "previous": "...", "results": [ { "log_id": "...", "timestamp": "...", "name": "...", "status": "...", "user": {...}, "project": {...}, "phase": {...}, "task": {...}, "details": {...} }, ... ] }`

