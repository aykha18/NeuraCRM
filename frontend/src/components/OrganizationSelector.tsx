import React, { useState, useEffect } from 'react';
import { ChevronDown, Building2 } from 'lucide-react';

interface Organization {
  id: number;
  name: string;
  domain?: string;
}

interface OrganizationSelectorProps {
  currentOrgId?: number;
  onOrganizationChange: (orgId: number) => void;
}

const OrganizationSelector: React.FC<OrganizationSelectorProps> = ({
  currentOrgId,
  onOrganizationChange
}) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  useEffect(() => {
    if (currentOrgId && organizations.length > 0) {
      const org = organizations.find(o => o.id === currentOrgId);
      setSelectedOrg(org || organizations[0]);
    }
  }, [currentOrgId, organizations]);

  const fetchOrganizations = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/organizations`);
      if (response.ok) {
        const orgs = await response.json();
        setOrganizations(orgs);
        if (orgs.length > 0 && !selectedOrg) {
          setSelectedOrg(orgs[0]);
          onOrganizationChange(orgs[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrgSelect = (org: Organization) => {
    setSelectedOrg(org);
    onOrganizationChange(org.id);
    setIsOpen(false);
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-gray-600">
        <Building2 className="w-4 h-4" />
        <span className="text-sm">Loading...</span>
      </div>
    );
  }

  if (organizations.length === 0) {
    return (
      <div className="flex items-center space-x-2 text-gray-600">
        <Building2 className="w-4 h-4" />
        <span className="text-sm">No organizations</span>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <Building2 className="w-4 h-4 text-gray-600" />
        <span className="text-gray-900">{selectedOrg?.name || 'Select Organization'}</span>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-300 rounded-lg shadow-lg z-50">
          <div className="py-1">
            {organizations.map((org) => (
              <button
                key={org.id}
                onClick={() => handleOrgSelect(org)}
                className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center space-x-2 ${
                  selectedOrg?.id === org.id ? 'bg-blue-50 text-blue-600' : 'text-gray-900'
                }`}
              >
                <Building2 className="w-4 h-4" />
                <div>
                  <div className="font-medium">{org.name}</div>
                  {org.domain && (
                    <div className="text-xs text-gray-500">{org.domain}</div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizationSelector;
