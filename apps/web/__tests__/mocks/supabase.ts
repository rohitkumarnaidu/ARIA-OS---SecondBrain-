import { vi } from 'vitest'
import type { SupabaseClient } from '@supabase/supabase-js'

type QueryResult<T = unknown> = { data: T | null; error: Error | null }

interface FilterState {
  column?: string
  value?: unknown
  method?: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'like' | 'ilike' | 'in' | 'is'
}

interface SupabaseQueryBuilder {
  select: ReturnType<typeof vi.fn>
  insert: ReturnType<typeof vi.fn>
  update: ReturnType<typeof vi.fn>
  delete: ReturnType<typeof vi.fn>
  upsert: ReturnType<typeof vi.fn>
  eq: ReturnType<typeof vi.fn>
  neq: ReturnType<typeof vi.fn>
  gt: ReturnType<typeof vi.fn>
  gte: ReturnType<typeof vi.fn>
  lt: ReturnType<typeof vi.fn>
  lte: ReturnType<typeof vi.fn>
  like: ReturnType<typeof vi.fn>
  ilike: ReturnType<typeof vi.fn>
  in: ReturnType<typeof vi.fn>
  is: ReturnType<typeof vi.fn>
  order: ReturnType<typeof vi.fn>
  range: ReturnType<typeof vi.fn>
  limit: ReturnType<typeof vi.fn>
  single: ReturnType<typeof vi.fn>
  maybeSingle: ReturnType<typeof vi.fn>
  textSearch: ReturnType<typeof vi.fn>
  filter: ReturnType<typeof vi.fn>
  or: ReturnType<typeof vi.fn>
  not: ReturnType<typeof vi.fn>
  match: ReturnType<typeof vi.fn>
  execute: ReturnType<typeof vi.fn>
  then: (resolve: (value: QueryResult) => QueryResult) => Promise<QueryResult>
  _tableName: string
}

function createQueryBuilder(tableName: string): SupabaseQueryBuilder {
  const self: SupabaseQueryBuilder = {
    _tableName: tableName,
    select: vi.fn(() => self),
    insert: vi.fn(() => self),
    update: vi.fn(() => self),
    delete: vi.fn(() => self),
    upsert: vi.fn(() => self),
    eq: vi.fn(() => self),
    neq: vi.fn(() => self),
    gt: vi.fn(() => self),
    gte: vi.fn(() => self),
    lt: vi.fn(() => self),
    lte: vi.fn(() => self),
    like: vi.fn(() => self),
    ilike: vi.fn(() => self),
    in: vi.fn(() => self),
    is: vi.fn(() => self),
    order: vi.fn(() => self),
    range: vi.fn(() => self),
    limit: vi.fn(() => self),
    single: vi.fn(() => self),
    maybeSingle: vi.fn(() => self),
    textSearch: vi.fn(() => self),
    filter: vi.fn(() => self),
    or: vi.fn(() => self),
    not: vi.fn(() => self),
    match: vi.fn(() => self),
    execute: vi.fn(() => Promise.resolve({ data: null, error: null })),
    then(resolve) {
      return Promise.resolve(resolve({ data: null, error: null }))
    },
  }
  return self
}

interface SupabaseAuthMock {
  getSession: ReturnType<typeof vi.fn>
  setSession: ReturnType<typeof vi.fn>
  signUp: ReturnType<typeof vi.fn>
  signInWithPassword: ReturnType<typeof vi.fn>
  signInWithOAuth: ReturnType<typeof vi.fn>
  signOut: ReturnType<typeof vi.fn>
  getUser: ReturnType<typeof vi.fn>
  onAuthStateChange: ReturnType<typeof vi.fn>
  refreshSession: ReturnType<typeof vi.fn>
  resetPasswordForEmail: ReturnType<typeof vi.fn>
  updateUser: ReturnType<typeof vi.fn>
  get user(): null
  get session(): null
}

interface SupabaseStorageMock {
  from: ReturnType<typeof vi.fn>
}

interface SupabaseRealtimeMock {
  channel: ReturnType<typeof vi.fn>
  removeChannel: ReturnType<typeof vi.fn>
  removeAllChannels: ReturnType<typeof vi.fn>
}

interface SupabaseFunctionsMock {
  invoke: ReturnType<typeof vi.fn>
}

interface SupabaseMock {
  from: ReturnType<typeof vi.fn>
  auth: SupabaseAuthMock
  storage: SupabaseStorageMock
  channel: ReturnType<typeof vi.fn>
  removeChannel: ReturnType<typeof vi.fn>
  removeAllChannels: ReturnType<typeof vi.fn>
  functions: SupabaseFunctionsMock
  rpc: ReturnType<typeof vi.fn>
}

function createAuthMock(): SupabaseAuthMock {
  return {
    getSession: vi.fn(() =>
      Promise.resolve({ data: { session: null }, error: null }),
    ),
    setSession: vi.fn(() =>
      Promise.resolve({ data: { session: null }, error: null }),
    ),
    signUp: vi.fn(() =>
      Promise.resolve({ data: { user: null, session: null }, error: null }),
    ),
    signInWithPassword: vi.fn(() =>
      Promise.resolve({ data: { user: null, session: null }, error: null }),
    ),
    signInWithOAuth: vi.fn(() =>
      Promise.resolve({ data: { provider: 'google', url: 'http://localhost:3000/auth/callback' }, error: null }),
    ),
    signOut: vi.fn(() => Promise.resolve({ error: null })),
    getUser: vi.fn(() =>
      Promise.resolve({
        data: {
          user: {
            id: 'test-user-id',
            email: 'test@example.com',
            aud: 'authenticated',
            role: 'authenticated',
            created_at: new Date().toISOString(),
          },
        },
        error: null,
      }),
    ),
    onAuthStateChange: vi.fn(() => ({
      data: { subscription: { unsubscribe: vi.fn() } },
    })),
    refreshSession: vi.fn(() =>
      Promise.resolve({ data: { session: null }, error: null }),
    ),
    resetPasswordForEmail: vi.fn(() =>
      Promise.resolve({ data: {}, error: null }),
    ),
    updateUser: vi.fn(() =>
      Promise.resolve({ data: { user: null }, error: null }),
    ),
    get user() {
      return null
    },
    get session() {
      return null
    },
  }
}

export function createMockSupabase(): SupabaseMock {
  const queryBuilders = new Map<string, SupabaseQueryBuilder>()

  const mock: SupabaseMock = {
    from: vi.fn((table: string) => {
      if (!queryBuilders.has(table)) {
        queryBuilders.set(table, createQueryBuilder(table))
      }
      return queryBuilders.get(table)!
    }),
    auth: createAuthMock(),
    storage: {
      from: vi.fn(() => ({
        upload: vi.fn(() => Promise.resolve({ data: { path: '' }, error: null })),
        download: vi.fn(() => Promise.resolve({ data: new Blob(), error: null })),
        remove: vi.fn(() => Promise.resolve({ data: {}, error: null })),
        list: vi.fn(() => Promise.resolve({ data: [], error: null })),
        getPublicUrl: vi.fn(() => ({ data: { publicUrl: 'http://localhost:3000/file' } })),
      })),
    },
    channel: vi.fn(() => ({
      on: vi.fn(() => ({
        subscribe: vi.fn(() => Promise.resolve('SUBSCRIBED')),
        unsubscribe: vi.fn(),
      })),
      subscribe: vi.fn(() => Promise.resolve('SUBSCRIBED')),
      unsubscribe: vi.fn(),
    })),
    removeChannel: vi.fn(() => Promise.resolve()),
    removeAllChannels: vi.fn(() => Promise.resolve()),
    functions: {
      invoke: vi.fn(() => Promise.resolve({ data: null, error: null })),
    },
    rpc: vi.fn(() =>
      Promise.resolve({ data: null, error: null }),
    ),
  }

  return mock
}

export type { SupabaseMock, SupabaseQueryBuilder, SupabaseAuthMock }
