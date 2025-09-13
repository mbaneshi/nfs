import React from 'react'
import { useGetHealthQuery } from '../services/api'

export const Dashboard: React.FC = () => {
  const { data: health, isLoading, error } = useGetHealthQuery()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Welcome to NSF Multi-Platform AI Automation Template
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-green-600 rounded-full"></div>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  API Status
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {isLoading ? 'Loading...' : error ? 'Error' : health?.status || 'Unknown'}
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Automation Platform
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  n8n Ready
                </dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Database
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  Supabase Connected
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <button className="btn btn-primary">
            Create Workflow
          </button>
          <button className="btn btn-secondary">
            View Analytics
          </button>
          <button className="btn btn-secondary">
            Manage Users
          </button>
          <button className="btn btn-secondary">
            Settings
          </button>
        </div>
      </div>
    </div>
  )
}
