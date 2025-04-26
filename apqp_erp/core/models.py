import uuid
from django.db import models
# from django.contrib.auth.models import User # Option 1
# from django.contrib.auth.models import AbstractUser # Option 2

# --- Constants for Choices ---

PROJECT_STATUS_CHOICES = [
    ('Planning', 'Planning'),
    ('Active', 'Active'),
    ('Completed', 'Completed'),
    ('OnHold', 'On Hold'),
]

PHASE_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('InProgress', 'In Progress'),
    ('Review', 'In Review'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
]

# Simplified Project-level permissions for MVP
PROJECT_PERMISSION_LEVEL_CHOICES = [
    ('Read', 'Read Only'),
    ('Edit', 'Edit Project/Phases'), # Can modify project details, phase status, docs
    ('Manage', 'Manage Team/Permissions'), # Can change team, responsible user, permissions
    ('Admin', 'Full Control'),
]

TASK_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('InProgress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Blocked', 'Blocked'),
]

LOG_STATUS_CHOICES = [
    ('Info', 'Info'),
    ('Action', 'Action'),
    ('Alert', 'Alert'),
]

# --- Models ---

class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    department_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    # M2M to Team defined in Team model
    # M2M for Project Permissions defined in Project model

    def __str__(self):
        return self.name

class Team(models.Model):
    team_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    members = models.ManyToManyField(
        User,
        related_name='teams',
        blank=True
    )

    def __str__(self):
        return self.name

# Client is now independent and can be linked to multiple projects
class Client(models.Model):
    client_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True) # Unique email across all clients
    # Other general client info can be added here if needed
    # M2M to Project defined in Project model

    def __str__(self):
        return self.name

class Project(models.Model):
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=PROJECT_STATUS_CHOICES,
        default='Planning'
    )
    responsible_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='responsible_projects',
        null=True,
        blank=True
    )
    team = models.ForeignKey( # A project still has one primary team
        Team,
        on_delete=models.SET_NULL,
        related_name='projects',
        null=True,
        blank=True
    )
    # Link to Clients (Many-to-Many)
    clients = models.ManyToManyField(
        Client,
        related_name='projects',
        blank=True,
        # Optional: Add a 'through' model if you need to store role/info specific to the Project-Client relationship
        # through='ProjectClientMembership'
    )
    # Users with specific permissions on this project
    users_with_permission = models.ManyToManyField(
        User,
        through='ProjectPermission',
        related_name='projects_with_access',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Model for Project-level permissions (replaces PhasePermission)
class ProjectPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    permission_level = models.CharField(
        max_length=50,
        choices=PROJECT_PERMISSION_LEVEL_CHOICES,
        default='Read'
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.project.name} ({self.get_permission_level_display()})"

    class Meta:
        unique_together = ('user', 'project') # User has one permission level per project

class PhaseTemplate(models.Model):
    template_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    # Content now likely includes definitions for standard tasks for this template type
    content = models.JSONField(default=dict, help_text="Defines phase structure, fields, and potentially standard task definitions.")
    applicable_level = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Phase(models.Model):
    phase_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='phases'
    )
    level = models.IntegerField(help_text="Sequential level (e.g., 1, 2).")
    status = models.CharField(
        max_length=50,
        choices=PHASE_STATUS_CHOICES,
        default='Pending'
    )
    # Configuration derived from template, might specify required tasks/fields
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON describing the specific structure/fields for this phase instance."
    )
    # Simplified documents list (can be enhanced later)
    documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of associated documents (e.g., [{name: 'spec.pdf', id: '...', url: '...'}])."
    )
    # Note: Phase-specific permissions removed, use ProjectPermission now.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Phase {self.level} ({self.project.name})"

    class Meta:
        ordering = ['project', 'level']
        unique_together = ('project', 'level')

# New Task Model
class Task(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE, # Task belongs to a phase
        related_name='tasks'
    )
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # Keep task if user deleted, needs reassignment
        related_name='assigned_tasks',
        null=True,
        blank=True # Task might be unassigned initially
    )
    name = models.CharField(max_length=255, help_text="Concise name or title of the task.")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=TASK_STATUS_CHOICES,
        default='Pending'
    )
    due_date = models.DateField(null=True, blank=True)
    # Optional: Link back to a definition key in Phase.configuration if needed
    # task_definition_key = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        assignee = f" to {self.assigned_user.name}" if self.assigned_user else " (Unassigned)"
        return f"Task: {self.name} [{self.status}] (Phase {self.phase.level} - {self.phase.project.name}){assignee}"

    class Meta:
        ordering = ['phase__project', 'phase__level', 'created_at'] # Order globally by project, phase, then creation


class HistoryLog(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='history_logs'
    )
    # Optional link to phase if action is phase-specific
    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE,
        related_name='history_logs',
        null=True,
        blank=True
    )
    # Optional link to task if action is task-specific
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL, # Keep log if task is deleted, show task was involved
        related_name='history_logs',
        null=True,
        blank=True
    )
    # User performing action (null for system)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='history_logs',
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    # Human-readable summary of the action
    name = models.TextField(help_text="Summary of the action (e.g., 'Task assigned to X', 'Permission Granted').")
    # Type/Severity (Info, Action, Alert) - Set by the process creating the log
    status = models.CharField(
        max_length=50,
        choices=LOG_STATUS_CHOICES,
        default='Info',
        help_text="Type or severity of the log."
    )
    # Optional JSON for extra context (e.g., changed fields, target user)
    details = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        target = f"Project: {self.project.name}"
        if self.phase:
            target += f", Phase: {self.phase.level}"
        if self.task:
             target += f", Task: {self.task.name[:30]}..." # Truncate task name
        actor = f"User: {self.user.name}" if self.user else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] ({self.status}) {actor} - {self.name} on {target}"

    class Meta:
        ordering = ['-timestamp']