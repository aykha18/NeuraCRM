import React from 'react';

const KanbanBoard = () => {
  return (
    <div className="p-4 grid grid-cols-3 gap-4">
      {['To Do', 'In Progress', 'Done'].map((column) => (
        <div key={column} className="bg-gray-100 rounded-xl shadow p-2">
          <h2 className="text-lg font-semibold mb-2">{column}</h2>
          {/* Tasks go here */}
        </div>
      ))}
    </div>
  );
};

export default KanbanBoard;
