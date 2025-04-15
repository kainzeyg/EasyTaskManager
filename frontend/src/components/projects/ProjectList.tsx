import { Project } from '../../types/types';

interface ProjectListProps {
  projects: Project[];
  selectedProject: number | null;
  onSelect: (id: number) => void;
}

const ProjectList = ({ projects, selectedProject, onSelect }: ProjectListProps) => {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Проекты</h2>
      <ul className="space-y-2">
        {projects.map((project) => (
          <li key={project.id}>
            <button
              onClick={() => onSelect(project.id)}
              className={`w-full text-left p-2 rounded ${selectedProject === project.id ? 'bg-primary text-white' : 'hover:bg-gray-100'}`}
            >
              {project.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProjectList;