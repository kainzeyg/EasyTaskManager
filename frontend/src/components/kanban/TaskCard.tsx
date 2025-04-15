import { Draggable } from 'react-beautiful-dnd';


const TaskCard = ({ task, index }: { task: any; index: number }) => {
  return (
    <Draggable draggableId={task.id.toString()} index={index}>
      {(provided) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className="bg-white p-3 rounded shadow"
        >
          <h4 className="font-medium">{task.name}</h4>
          {task.description && (
            <p className="text-sm text-gray-600 mt-1">{task.description}</p>
          )}
        </div>
      )}
    </Draggable>
  );
};

export default TaskCard;  