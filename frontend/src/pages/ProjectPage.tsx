import { useParams } from 'react-router-dom';
import Board from '../components/kanban/Board';
import { useQuery } from '@tanstack/react-query';
import { getProjectTasks } from '../api/tasks';
import Loader from '../components/ui/Loader';

const ProjectPage = () => {
  const { projectId } = useParams();
  const { data: tasks, isLoading } = useQuery(
    ['tasks', projectId],
    () => getProjectTasks(Number(projectId)),
    { enabled: !!projectId }
  );

  if (isLoading) return <Loader />;

  return (
    <div className="p-4">
      <Board tasks={tasks || []} projectId={Number(projectId)} />
    </div>
  );
};

export default ProjectPage;