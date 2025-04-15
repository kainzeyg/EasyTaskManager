import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Board from '../components/kanban/Board';
import ProjectList from '../components/projects/ProjectList';
import { getProjectTasks } from '../api/tasks';
import { getProjects } from '../api/projects';

const DashboardPage = () => {
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  
  const { data: projects } = useQuery(['projects'], getProjects);
  const { data: tasks } = useQuery(
    ['tasks', selectedProject],
    () => getProjectTasks(selectedProject!),
    { enabled: !!selectedProject }
  );

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-64 bg-white shadow-md">
        <ProjectList 
          projects={projects || []} 
          onSelect={setSelectedProject}
          selectedProject={selectedProject}
        />
      </div>
      
      <div className="flex-1 overflow-hidden">
        {selectedProject ? (
          <Board tasks={tasks || []} projectId={selectedProject} />
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">Выберите проект для просмотра задач</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;