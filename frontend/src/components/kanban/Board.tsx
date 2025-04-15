import { DragDropContext, DropResult } from 'react-beautiful-dnd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import Column from './Column';
import { updateTaskStatus } from '../../api/tasks';
import { Task, TaskStatus } from '../../types/types';

const Board = ({ tasks, projectId }: { tasks: Task[]; projectId: number }) => {
  const queryClient = useQueryClient();
  
  const statusMutation = useMutation(updateTaskStatus, {
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', projectId]);
    },
  });

  const onDragEnd = (result: DropResult) => {
    if (!result.destination) return;
    
    const taskId = Number(result.draggableId);
    const newStatus = result.destination.droppableId as TaskStatus;
    
    statusMutation.mutate({ taskId, status: newStatus });
  };

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="flex space-x-4 p-4 h-full overflow-x-auto">
        {['Новая', 'В работе', 'Тестирование', 'Готова к релизу', 'Выполнена'].map((status) => (
          <Column 
            key={status}
            status={status}
            tasks={tasks.filter(task => task.status === status)}
          />
        ))}
      </div>
    </DragDropContext>
  );
};

export default Board;