import {createClient} from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL || 'https://db.edcopo.info';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'your_supabase_anon_key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const apiClient = {
  baseURL: process.env.API_URL || 'https://api.edcopo.info',
  
  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = await supabase.auth.getSession();
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token.data.session?.access_token && {
          Authorization: `Bearer ${token.data.session.access_token}`,
        }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  },

  async get(endpoint: string) {
    return this.request(endpoint, {method: 'GET'});
  },

  async post(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async put(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async delete(endpoint: string) {
    return this.request(endpoint, {method: 'DELETE'});
  },
};
