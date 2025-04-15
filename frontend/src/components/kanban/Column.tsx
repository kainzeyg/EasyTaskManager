import { Droppable } from 'react-beautiful-dnd';
import TaskCard from './TaskCard';

const Column = ({ status, tasks }: { status: string; tasks: any[] }) => {
  return (
    <Droppable droppableId={status}>
      {(provided) => (
        <div
          ref={provided.innerRef}
          {...provided.droppableProps}
          className="w-64 bg-column rounded-lg p-3"
        >
          <h3 className="font-semibold mb-3">{status}</h3>
          <div className="space-y-3">
            {tasks.map((task, index) => (
              <TaskCard key={task.id} task={task} index={index} />
            ))}
            {provided.placeholder}
          </div>
        </div>
      )}
    </Droppable>
  );
};

export default Column; // Добавьте default export