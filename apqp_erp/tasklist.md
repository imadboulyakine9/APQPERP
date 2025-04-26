Okay, here is a prioritized list of tasks to build the Minimum Viable Product (MVP), focusing on delivering core functionality first. This assumes you are using Django and Django REST Framework (DRF).

# MVP Task List (Ordered)

## Phase 1: Foundation & Core Models

1.  **Project Setup:**
    *   Initialize Django project (`django-admin startproject`).
    *   Initialize core app (`./manage.py startapp core` or similar).
    *   Configure `settings.py` (Database, Installed Apps, Timezone, Static/Media files).
    *   Set up basic requirements (`requirements.txt`).
    *   Initialize Git repository.

2.  **Core Model Implementation:**
    *   Define `User`, `Team`, `Client`, `Project`, `ProjectPermission`, `Phase`, `Task`, `Document` models in `models.py`.
    *   Ensure relationships (`ForeignKey`, `ManyToManyField`, `through`) are correctly defined.
    *   Define model `__str__` methods for readability.
    *   Define choices constants (e.g., `PROJECT_STATUS_CHOICES`).

3.  **Database Migrations:**
    *   Run `makemigrations` to create initial migration files based on models.
    *   Run `migrate` to apply the schema to the database.

4.  **Basic Authentication Setup:**
    *   Choose an authentication method (e.g., DRF's `TokenAuthentication` or `django-rest-knox`, `djangorestframework-simplejwt`).
    *   Implement basic Login API endpoint (`/api/v1/auth/login/`).
    *   Configure DRF default authentication classes.

5.  **Admin Interface Setup:**
    *   Register all core models (`User`, `Team`, `Client`, `Project`, `Phase`, `Task`, `Document`, `ProjectPermission`) in `admin.py`.
    *   Create a superuser (`./manage.py createsuperuser`).
    *   Use the admin interface to create initial test data (Users, Teams).

## Phase 2: Core CRUD APIs & Permissions

6.  **User & Team APIs:**
    *   API: Get Current User (`GET /api/v1/users/me/`).
    *   API: Create Team (`POST /api/v1/teams/`).
    *   API: List Teams (`GET /api/v1/teams/`).
    *   API: Get Team Details (`GET /api/v1/teams/{team_id}/`).
    *   API: Add/Remove Team Members (`POST /teams/{id}/members/`, `DELETE /teams/{id}/members/{user_id}/`).
    *   *Focus:* Basic creation and viewing. Membership management is important for project assignment.

7.  **Project APIs & Permissions (Core Loop):**
    *   API: Create Project (`POST /api/v1/projects/`) - **Crucial:** Implement permission check (e.g., only 'Manager' role can create). Assign initial 'Admin' `ProjectPermission` to the creator. Link `Team`, `responsible_user`.
    *   API: List Projects (`GET /api/v1/projects/`) - **Crucial:** Implement filtering logic to only show projects the requesting user has *any* `ProjectPermission` for, or is the `responsible_user`, or is in the assigned `Team`.
    *   API: Get Project Details (`GET /api/v1/projects/{project_id}/`) - Implement permission check (user needs read access via `ProjectPermission`).
    *   API: Update Project (`PATCH /api/v1/projects/{project_id}/`) - Implement permission check ('Edit' or higher required).

8.  **Project Permission Management APIs:**
    *   API: List Project Permissions (`GET /api/v1/projects/{project_id}/permissions/`) - Implement permission check ('Manage' or 'Admin' required).
    *   API: Set/Update User Permission (`PUT /api/v1/projects/{project_id}/permissions/{user_id}/`) - Implement permission check ('Manage' or 'Admin' required).
    *   API: Revoke User Permission (`DELETE /api/v1/projects/{project_id}/permissions/{user_id}/`) - Implement permission check ('Manage' or 'Admin' required).
    *   *Focus:* Enable basic access control after project creation.

## Phase 3: Phase, Task & Document Management

9.  **Phase APIs (Nested under Projects):**
    *   API: List Phases (`GET /projects/{project_id}/phases/`) - Check project read permission.
    *   API: Create Phase (`POST /projects/{project_id}/phases/`) - Check project edit permission.
    *   API: Get Phase Details (`GET /projects/{project_id}/phases/{phase_id}/`) - Check project read permission.
    *   API: Update Phase (`PATCH /projects/{project_id}/phases/{phase_id}/`) - Check project edit permission (e.g., for changing status).

10. **Document Handling & APIs:**
    *   Configure `MEDIA_ROOT` and `MEDIA_URL` properly in `settings.py`.
    *   Configure URL patterns for serving media files during development.
    *   API: Upload Document (`POST /projects/{project_id}/phases/{phase_id}/documents/`) - Handle `multipart/form-data`, check project edit permission, save file, create `Document` record.
    *   API: List Documents (`GET /projects/{project_id}/phases/{phase_id}/documents/`) - Check project read permission. Return file URL.
    *   API: Delete Document (`DELETE /documents/{document_id}/`) - Check project edit permission, delete DB record *and* the physical file.

11. **Task APIs:**
    *   API: Create Task (`POST /projects/{project_id}/phases/{phase_id}/tasks/`) - Check project edit permission.
    *   API: List Tasks for Phase (`GET /projects/{project_id}/phases/{phase_id}/tasks/`) - Check project read permission.
    *   API: Get Task Details (`GET /projects/{project_id}/phases/{phase_id}/tasks/{task_id}/`) - Check project read permission.
    *   API: Update Task (`PATCH /projects/{project_id}/phases/{phase_id}/tasks/{task_id}/`) - Check project edit permission OR if user is `assigned_user` (for status changes).
    *   API: **Get My Tasks (`GET /users/me/tasks/`)** - **Crucial user-facing feature.** Filter tasks where `assigned_user` is the current user.

## Phase 4: Supporting Features & Polish

12. **Client APIs:**
    *   Implement basic CRUD APIs for Clients (`POST`, `GET /clients/`, `GET /clients/{id}/`).
    *   Modify Project Create/Update APIs to handle `client_ids` linking.

13. **History Log Implementation:**
    *   API: List History Logs (`GET /api/v1/history-logs/`) - Implement filtering by `project_id` (required) and check project access. Implement pagination.
    *   **Backend Logic:** Integrate `HistoryLog.objects.create(...)` calls into relevant API views or model `save` methods (use signals cautiously) for key events:
        *   Project Created/Updated (Status, Responsible User, Team change)
        *   Phase Created/Updated (Status change)
        *   Task Created/Assigned/Status Changed/Completed
        *   Document Uploaded/Deleted
        *   Permission Granted/Revoked

14. **Phase Template Read APIs:**
    *   Use Django Admin to create a few `PhaseTemplate` examples.
    *   API: List Templates (`GET /api/v1/phase-templates/`).
    *   API: Get Template Details (`GET /api/v1/phase-templates/{template_id}/`).
    *   *(Note: Automating Phase creation from templates is likely Post-MVP)*.

15. **Basic Frontend/Testing:**
    *   Develop a minimal frontend (or use tools like Postman/Insomnia) to test *all* API endpoints and workflows.
    *   Write basic automated tests (e.g., using Django's `TestCase` or DRF's `APITestCase`) for critical paths like authentication, project creation, permission checks, and listing user tasks.

## Post-MVP Considerations (Not in this list)

*   Advanced filtering/sorting on list endpoints.
*   Real-time notifications (WebSockets).
*   Automated phase creation based on templates.
*   Complex reporting or dashboards.
*   Password reset functionality.
*   User invitation system.
*   More granular permissions (e.g., document-level).
*   Full-featured frontend UI.

This order focuses on building the core data structures and access controls first, then layering the main workflow elements (phases, tasks, documents), and finally adding supporting elements like clients and history logging. Remember to test continuously!
