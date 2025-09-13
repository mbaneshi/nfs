import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_URL || 'https://api.edcopo.info',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token')
      if (token) {
        headers.set('authorization', `Bearer ${token}`)
      }
      return headers
    },
  }),
  tagTypes: ['User', 'Automation', 'Workflow'],
  endpoints: (builder) => ({
    getHealth: builder.query<{ status: string }, void>({
      query: () => '/health',
    }),
    getWorkflows: builder.query<any[], void>({
      query: () => '/workflows',
      providesTags: ['Workflow'],
    }),
  }),
})

export const { useGetHealthQuery, useGetWorkflowsQuery } = apiSlice
