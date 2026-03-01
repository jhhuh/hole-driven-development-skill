interface TodoItem {
  id: string;
  text: string;
  completed: boolean;
}

interface TodoListProps {
  items: TodoItem[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  filter: 'all' | 'active' | 'completed';
}

// Return an HTML string representation of the todo list
export function renderTodoList(props: TodoListProps): string {
  const filtered = filterItems(props.items, props.filter);
  const listHtml = renderList(filtered);
  return assembleHtml(listHtml, filtered.length, props.items.length);
}

function filterItems(items: TodoItem[], filter: 'all' | 'active' | 'completed'): TodoItem[] {
  switch (filter) {
    case 'all': return items;
    case 'active': return items.filter(i => !i.completed);
    case 'completed': return items.filter(i => i.completed);
  }
}

function renderItem(item: TodoItem): string {
  const checked = item.completed ? ' checked' : '';
  const cls = item.completed ? ' class="completed"' : '';
  return `<li${cls} data-id="${item.id}">` +
    `<input type="checkbox"${checked} data-action="toggle" data-id="${item.id}">` +
    `<span>${item.text}</span>` +
    `<button data-action="delete" data-id="${item.id}">Delete</button>` +
    `</li>`;
}

function renderList(items: TodoItem[]): string {
  return `<ul>${items.map(renderItem).join('')}</ul>`;
}

function assembleHtml(listHtml: string, visibleCount: number, totalCount: number): string {
  return `<div class="todo-list">` +
    listHtml +
    `<p class="todo-count">${visibleCount} of ${totalCount} items</p>` +
    `</div>`;
}
