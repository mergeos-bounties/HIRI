import React, { useMemo, useState } from 'react';
import { Search, ChevronDown, ChevronRight, Grid, List, X, Home, Compass } from 'lucide-react';

export interface EntityDevice {
  id: string;
  name: string;
  type: string;
  area?: string;
  room?: string;
  status: 'online' | 'offline' | 'warning';
  value?: string | number;
  unit?: string;
  tags?: string[];
}

export interface DashboardProps {
  devices: EntityDevice[];
  onToggleDevice?: (id: string) => void;
  title?: string;
}

export const Dashboard: React.FC<DashboardProps> = ({
  devices = [],
  onToggleDevice,
  title = "System Control Dashboard"
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Filter devices based on search query
  const filteredDevices = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return devices;

    return devices.filter((device) => {
      const matchName = device.name.toLowerCase().includes(q);
      const matchId = device.id.toLowerCase().includes(q);
      const matchRoom = (device.room || '').toLowerCase().includes(q);
      const matchArea = (device.area || '').toLowerCase().includes(q);
      const matchType = device.type.toLowerCase().includes(q);
      const matchTags = device.tags?.some((t) => t.toLowerCase().includes(q));

      return matchName || matchId || matchRoom || matchArea || matchType || matchTags;
    });
  }, [devices, searchQuery]);

  // Group devices by Area/Room hierarchy
  const groupedDevices = useMemo(() => {
    const groups: Record<string, EntityDevice[]> = {};

    filteredDevices.forEach((device) => {
      const areaName = device.area || 'General';
      const roomName = device.room ? `${areaName} • ${device.room}` : areaName;

      if (!groups[roomName]) {
        groups[roomName] = [];
      }
      groups[roomName].push(device);
    });

    // Sort group keys alphabetically, keeping "General" at the end if present
    return Object.keys(groups)
      .sort((a, b) => {
        if (a === 'General') return 1;
        if (b === 'General') return -1;
        return a.localeCompare(b);
      })
      .reduce((acc, key) => {
        acc[key] = groups[key];
        return acc;
      }, {} as Record<string, EntityDevice[]>);
  }, [filteredDevices]);

  const toggleGroupCollapse = (groupName: string) => {
    setCollapsedGroups((prev) => ({
      ...prev,
      [groupName]: !prev[groupName]
    }));
  };

  const clearSearch = () => setSearchQuery('');

  return (
    <div className="w-full min-h-screen bg-slate-900 text-slate-100 p-4 md:p-8 font-sans">
      {/* Header & Search Bar Section */}
      <header className="max-w-7xl mx-auto mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white flex items-center gap-2">
            <Home className="w-7 h-7 text-indigo-400" />
            {title}
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Managing {devices.length} total entities across {Object.keys(groupedDevices).length} active regions
          </p>
        </div>

        {/* Search & Layout Controls */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search rooms, areas, devices, tags..."
              className="w-full bg-slate-800 border border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg pl-9 pr-9 py-2 text-sm text-white placeholder-slate-400 outline-none transition-all"
            />
            {searchQuery && (
              <button
                onClick={clearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                aria-label="Clear search"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
              title="Grid View"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded ${viewMode === 'list' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
              title="List View"
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto space-y-6">
        {Object.keys(groupedDevices).length === 0 ? (
          <div className="text-center py-16 bg-slate-800/40 rounded-xl border border-slate-800 p-6">
            <Compass className="w-12 h-12 text-slate-500 mx-auto mb-3 animate-pulse" />
            <h3 className="text-lg font-medium text-slate-200">No matching rooms or devices found</h3>
            <p className="text-sm text-slate-400 mt-1">Try adjusting your search terms or filters</p>
            <button
              onClick={clearSearch}
              className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
            >
              Clear Search Query
            </button>
          </div>
        ) : (
          Object.entries(groupedDevices).map(([groupName, groupDevices]) => {
            const isCollapsed = !!collapsedGroups[groupName];

            return (
              <section key={groupName} className="bg-slate-800/60 rounded-xl border border-slate-800 overflow-hidden">
                {/* Group Header */}
                <div
                  onClick={() => toggleGroupCollapse(groupName)}
                  className="flex items-center justify-between p-4 bg-slate-800/80 cursor-pointer hover:bg-slate-800 transition-colors select-none"
                >
                  <div className="flex items-center gap-3">
                    {isCollapsed ? (
                      <ChevronRight className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                    <h2 className="text-base font-semibold text-slate-100">{groupName}</h2>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-slate-700 text-slate-300 font-medium">
                      {groupDevices.length}
                    </span>
                  </div>
                </div>

                {/* Group Body */}
                {!isCollapsed && (
                  <div className="p-4 border-t border-slate-800">
                    <div
                      className={
                        viewMode === 'grid'
                          ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4'
                          : 'flex flex-col gap-2'
                      }
                    >
                      {groupDevices.map((device) => (
                        <div
                          key={device.id}
                          onClick={() => onToggleDevice && onToggleDevice(device.id)}
                          className={`p-4 rounded-lg border transition-all ${
                            viewMode === 'grid' ? 'flex flex-col justify-between' : 'flex items-center justify-between'
                          } ${
                            device.status === 'online'
                              ? 'bg-slate-900/80 border-slate-700/80 hover:border-indigo-500/50'
                              : 'bg-slate-900/40 border-slate-800 text-slate-500'
                          }`}
                        >
                          <div>
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-medium text-slate-200 text-sm truncate">{device.name}</span>
                              <span
                                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                                  device.status === 'online'
                                    ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]'
                                    : device.status === 'warning'
                                    ? 'bg-amber-400'
                                    : 'bg-slate-600'
                                }`}
                              />
                            </div>
                            <p className="text-xs text-slate-400 mt-0.5">{device.type}</p>
                          </div>

                          {device.value !== undefined && (
                            <div className={viewMode === 'grid' ? 'mt-3 pt-2 border-t border-slate-800/60' : ''}>
                              <span className="text-sm font-semibold text-indigo-300">
                                {device.value} {device.unit || ''}
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            );
          })
        )}
      </main>
    </div>
  );
};

export default Dashboard;
