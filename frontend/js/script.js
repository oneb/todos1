const API_URL = "/api"; 

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const usernamePrompt = document.getElementById('username-prompt');
    const usernameForm = document.getElementById('username-form');
    const usernameInput = document.getElementById('username-input');
    const currentUsernameSpan = document.getElementById('current-username');
    const changeUsernameBtn = document.getElementById('change-username');
    const tasksDisplay = document.getElementById('tasks-display');
    const newTaskForm = document.getElementById('new-task-form');
    const taskTitleInput = document.getElementById('task-title');
    const tasksContainer = document.getElementById('tasks-container');
    
    // Check whether username has been provided. If not, prompt for username. 
    // If yes, show tasks for that user.
    const checkUsername = () => {
        const username = sessionStorage.getItem('username');
        if (username) {
            usernamePrompt.classList.add('hidden');
            tasksDisplay.classList.remove('hidden');
            currentUsernameSpan.textContent = username;
            updateTasksDisplay();
        } else {
            usernamePrompt.classList.remove('hidden');
            tasksDisplay.classList.add('hidden');
        }
    };

    // (re)load tasks for the current user and update tasks display
    async function updateTasksDisplay() {
        const username = sessionStorage.getItem('username');
        if (!username) return;

        const result = await apiRequest(`/tasks/?username=${encodeURIComponent(username)}`, 'GET', null, 'Failed to load tasks');
        
        if (result.success) {
            renderTasks(result.data);
        } else {
            console.error('Failed to load tasks:', result.status, result.message);
            tasksContainer.innerHTML = '<p class="error">Failed to load tasks.</p>';
        }
    }
    
    // Accept given username.
    usernameForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = usernameInput.value.trim();
        if (username) {
            sessionStorage.setItem('username', username);
            checkUsername();
        }
    });

    // Prompt for new username.
    changeUsernameBtn.addEventListener('click', () => {
        sessionStorage.removeItem('username');
        checkUsername();
        // Clear input field
        usernameInput.value = '';
    });

    // Add a new task
    newTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = taskTitleInput.value.trim();
        const username = sessionStorage.getItem('username');
        
        if (title && username) {
            await apiRequest('/tasks/', 'POST', {
                title,
                username,
                state: 'todo'
            }, 'Failed to create task');
            
            // Clear input field
            taskTitleInput.value = '';
            updateTasksDisplay();
        }
    });

    // Render tasks list to DOM
    function renderTasks(tasks) {
        tasksContainer.innerHTML = '';
        
        if (tasks.length === 0) {
            tasksContainer.innerHTML = '<p>No tasks yet. Create one!</p>';
            return;
        }

        tasks.forEach(task => {
            const li = document.createElement('li');
            li.classList.add(task.state);
            li.dataset.id = task.id;
            li.dataset.state = task.state;
            
            li.innerHTML = `
                <div class="task-checkbox">
                    <input type="checkbox" class="toggle-checkbox" data-id="${task.id}" data-state="${task.state}" ${task.state === 'done' ? 'checked' : ''}>
                </div>
                <span class="task-title">${task.title}</span>
                <div class="task-actions">
                    <button class="delete-btn" data-id="${task.id}">&times;</button>
                </div>
            `;
            
            tasksContainer.appendChild(li);
        });

        document.querySelectorAll('#tasks-container li').forEach(li => {
            // Edit task title on double click
            li.addEventListener('dblclick', function(e) {
                // Don't trigger for checkbox or delete button
                if (e.target.classList.contains('delete-btn') || e.target.closest('.delete-btn') || 
                    e.target.classList.contains('toggle-checkbox')) {
                    return;
                }
                
                const titleSpan = this.querySelector('.task-title');
                const currentText = titleSpan.textContent;
                const taskId = this.dataset.id;
                
                const inputField = document.createElement('input');
                inputField.type = 'text';
                inputField.value = currentText;
                inputField.className = 'task-title-edit';
                inputField.dataset.id = taskId;
                
                titleSpan.replaceWith(inputField);
                inputField.focus();
                
                // Save on pressing enter
                inputField.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        updateTaskTitle(taskId, this.value);
                    }
                });
                
                // Save on clicking elsewhere
                inputField.addEventListener('blur', function() {
                    updateTaskTitle(taskId, this.value);
                });
            });
        });

        // Toggle todo/done when clicking on checkbox
        document.querySelectorAll('.toggle-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', function(e) {
                // Prevent double-triggering
                e.stopPropagation();
                toggleTaskState(e);
            });
        });
        
        // Delete when clicking on "X"
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', deleteTask);
        });
    }

    // Generic API request
    async function apiRequest(endpoint, method, data = null, errorMessage = 'Operation failed') {
        try {
            let options = { method };
            
            if (data) {
                options = {
                    method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                };
            }
            
            const response = await fetch(`${API_URL}${endpoint}`, options);

            if (response.ok) {
                // Try to parse JSON response if present
                const responseData = await response.json().catch(() => null);
                return { success: true, data: responseData };
            } else {
                const errorData = await response.json().catch(() => null);
                const errorDetail = errorData?.detail || errorMessage;
                alert(`Error: ${errorDetail}`);
                return { 
                    success: false, 
                    error: errorData, 
                    status: response.status, 
                    message: errorDetail 
                };
            }
        } catch (error) {
            console.error(`API request error:`, error);
            alert(`${errorMessage}. Please try again.`);
            return { 
                success: false, 
                error,
                message: `${errorMessage}. Please try again.` 
            };
        }
    }
    
    // Toggle task state between 'todo' and 'done'
    async function toggleTaskState(e) {
        const taskId = e.target.dataset.id;
        const currentState = e.target.dataset.state;
        const newState = currentState === 'todo' ? 'done' : 'todo';
        
        // Update checkbox state without waiting for reload
        e.target.checked = newState === 'done';
        
        await apiRequest(`/tasks/${taskId}`, 'PUT', { state: newState }, 'Failed to update task state');
        updateTasksDisplay();
    }
    
    // Update task title
    async function updateTaskTitle(taskId, newTitle) {
        if (!newTitle.trim()) {
            // If empty title, reload tasks to revert to original
            updateTasksDisplay();
            return;
        }
        
        await apiRequest(`/tasks/${taskId}`, 'PUT', { title: newTitle }, 'Failed to update task title');
        updateTasksDisplay();
    }
    
    // Delete a task
    async function deleteTask(e) {
        const taskId = e.target.dataset.id;

        if (confirm('Are you sure you want to delete this task?')) {
            await apiRequest(`/tasks/${taskId}`, 'DELETE', null, 'Failed to delete task');
            updateTasksDisplay();
        }
    }

    // Initialize the app
    checkUsername();
});
