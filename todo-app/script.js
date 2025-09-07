// Todo List Application with Local Storage
class TodoApp {
    constructor() {
        this.tasks = this.loadTasks();
        this.currentFilter = 'all';
        this.editingTaskId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.render();
        this.updateStats();
    }

    bindEvents() {
        // Add task button and enter key
        document.getElementById('addTaskBtn').addEventListener('click', () => this.addTask());
        document.getElementById('taskInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addTask();
            }
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.setFilter(e.target.dataset.filter));
        });

        // Action buttons
        document.getElementById('clearCompletedBtn').addEventListener('click', () => this.clearCompleted());
        document.getElementById('clearAllBtn').addEventListener('click', () => this.clearAll());
    }

    addTask() {
        const input = document.getElementById('taskInput');
        const text = input.value.trim();
        
        if (!text) {
            this.showNotification('Please enter a task!', 'error');
            return;
        }

        const task = {
            id: Date.now(),
            text: text,
            completed: false,
            createdAt: new Date().toISOString()
        };

        this.tasks.unshift(task);
        this.saveTasks();
        this.render();
        this.updateStats();
        
        input.value = '';
        this.showNotification('Task added successfully!', 'success');
    }

    toggleTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            task.completedAt = task.completed ? new Date().toISOString() : null;
            this.saveTasks();
            this.render();
            this.updateStats();
            
            const message = task.completed ? 'Task completed! 🎉' : 'Task marked as pending';
            this.showNotification(message, 'success');
        }
    }

    startEdit(id) {
        if (this.editingTaskId !== null) {
            this.cancelEdit();
        }
        this.editingTaskId = id;
        this.render();
    }

    saveEdit(id, newText) {
        const text = newText.trim();
        if (!text) {
            this.showNotification('Task cannot be empty!', 'error');
            return;
        }

        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.text = text;
            task.updatedAt = new Date().toISOString();
            this.saveTasks();
            this.editingTaskId = null;
            this.render();
            this.showNotification('Task updated successfully!', 'success');
        }
    }

    cancelEdit() {
        this.editingTaskId = null;
        this.render();
    }

    deleteTask(id) {
        if (confirm('Are you sure you want to delete this task?')) {
            this.tasks = this.tasks.filter(t => t.id !== id);
            this.saveTasks();
            this.render();
            this.updateStats();
            this.showNotification('Task deleted successfully!', 'success');
        }
    }

    setFilter(filter) {
        this.currentFilter = filter;
        
        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        this.render();
    }

    clearCompleted() {
        const completedCount = this.tasks.filter(t => t.completed).length;
        if (completedCount === 0) {
            this.showNotification('No completed tasks to clear!', 'info');
            return;
        }

        if (confirm(`Are you sure you want to delete ${completedCount} completed task(s)?`)) {
            this.tasks = this.tasks.filter(t => !t.completed);
            this.saveTasks();
            this.render();
            this.updateStats();
            this.showNotification(`${completedCount} completed task(s) deleted!`, 'success');
        }
    }

    clearAll() {
        if (this.tasks.length === 0) {
            this.showNotification('No tasks to clear!', 'info');
            return;
        }

        if (confirm('Are you sure you want to delete ALL tasks? This action cannot be undone.')) {
            this.tasks = [];
            this.saveTasks();
            this.render();
            this.updateStats();
            this.showNotification('All tasks deleted!', 'success');
        }
    }

    getFilteredTasks() {
        switch (this.currentFilter) {
            case 'completed':
                return this.tasks.filter(t => t.completed);
            case 'pending':
                return this.tasks.filter(t => !t.completed);
            default:
                return this.tasks;
        }
    }

    render() {
        const taskList = document.getElementById('taskList');
        const emptyState = document.getElementById('emptyState');
        const filteredTasks = this.getFilteredTasks();

        if (filteredTasks.length === 0) {
            taskList.innerHTML = '';
            emptyState.classList.remove('hidden');
            
            // Update empty state message based on filter
            const emptyMessages = {
                all: '🎯 No tasks yet! Add your first task above.',
                pending: '✅ No pending tasks! Great job!',
                completed: '📝 No completed tasks yet. Get started!'
            };
            emptyState.querySelector('p').textContent = emptyMessages[this.currentFilter];
        } else {
            emptyState.classList.add('hidden');
            taskList.innerHTML = filteredTasks.map(task => this.renderTask(task)).join('');
        }
    }

    renderTask(task) {
        const isEditing = this.editingTaskId === task.id;
        
        return `
            <li class="task-item ${task.completed ? 'completed' : ''}" data-id="${task.id}">
                <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} 
                       onchange="todoApp.toggleTask(${task.id})">
                
                ${isEditing ? `
                    <input type="text" class="task-text" value="${this.escapeHtml(task.text)}" 
                           id="edit-input-${task.id}" maxlength="200">
                    <div class="task-actions">
                        <button class="task-btn save-btn" onclick="todoApp.saveEdit(${task.id}, document.getElementById('edit-input-${task.id}').value)">Save</button>
                        <button class="task-btn cancel-btn" onclick="todoApp.cancelEdit()">Cancel</button>
                    </div>
                ` : `
                    <span class="task-text">${this.escapeHtml(task.text)}</span>
                    <div class="task-actions">
                        <button class="task-btn edit-btn" onclick="todoApp.startEdit(${task.id})" title="Edit task">Edit</button>
                        <button class="task-btn delete-btn" onclick="todoApp.deleteTask(${task.id})" title="Delete task">Delete</button>
                    </div>
                `}
            </li>
        `;
    }

    updateStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(t => t.completed).length;
        const pending = total - completed;

        document.getElementById('totalTasks').textContent = total;
        document.getElementById('pendingTasks').textContent = pending;
        document.getElementById('completedTasks').textContent = completed;
    }

    loadTasks() {
        try {
            const tasks = localStorage.getItem('todoApp_tasks');
            return tasks ? JSON.parse(tasks) : [];
        } catch (error) {
            console.error('Error loading tasks from localStorage:', error);
            return [];
        }
    }

    saveTasks() {
        try {
            localStorage.setItem('todoApp_tasks', JSON.stringify(this.tasks));
        } catch (error) {
            console.error('Error saving tasks to localStorage:', error);
            this.showNotification('Error saving tasks. Storage might be full.', 'error');
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '6px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1000',
            maxWidth: '300px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            transform: 'translateX(350px)',
            transition: 'transform 0.3s ease'
        });

        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        // Add to DOM and animate in
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(350px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.todoApp = new TodoApp();
});

// Handle page visibility to sync data
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.todoApp) {
        // Reload tasks when page becomes visible (in case of updates in other tabs)
        const freshTasks = window.todoApp.loadTasks();
        if (JSON.stringify(freshTasks) !== JSON.stringify(window.todoApp.tasks)) {
            window.todoApp.tasks = freshTasks;
            window.todoApp.render();
            window.todoApp.updateStats();
        }
    }
});