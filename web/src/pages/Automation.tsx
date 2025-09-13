import React from 'react'

export const Automation: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Automation</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your AI-powered automation workflows
        </p>
      </div>

      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">n8n Integration</h2>
        <p className="text-gray-600 mb-4">
          Access your n8n automation platform to create and manage workflows.
        </p>
        <a
          href="https://automation.edcopo.info"
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          Open n8n Dashboard
        </a>
      </div>

      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">AI Services</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900">OpenAI</h3>
            <p className="text-sm text-gray-500 mt-1">
              GPT-4 integration for intelligent automation
            </p>
          </div>
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900">Anthropic Claude</h3>
            <p className="text-sm text-gray-500 mt-1">
              Claude integration for advanced AI workflows
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
