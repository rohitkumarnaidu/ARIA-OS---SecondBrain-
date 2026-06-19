'use client'

import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query'
import { api } from './client'

export function useApiQuery<T>(
  key: string[],
  path: string,
  config?: { params?: Record<string, string | number | boolean | undefined> },
  options?: Omit<UseQueryOptions<T>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<T>({
    queryKey: [...key, config?.params],
    queryFn: () => api.get<T>(path, { params: config?.params }),
    staleTime: 30 * 1000,
    retry: 2,
    ...options,
  })
}

export function useApiMutation<TData, TVariables = void>(
  path: string,
  method: 'post' | 'put' | 'patch' | 'delete' = 'post',
  options?: Omit<UseMutationOptions<TData, Error, TVariables>, 'mutationFn'>,
) {
  const queryClient = useQueryClient()

  return useMutation<TData, Error, TVariables>({
    mutationFn: async (variables) => {
      if (method === 'delete') {
        return api.delete<TData>(path)
      }
      return api[method]<TData>(path, variables as any)
    },
    ...options,
    onSuccess: (...args) => {
      queryClient.invalidateQueries()
      options?.onSuccess?.(...args)
    },
  })
}

import { useInfiniteQuery } from '@tanstack/react-query'

export function useApiInfiniteQuery<T>(
  key: string[],
  path: string,
  limit = 20,
  options?: Omit<Parameters<typeof useInfiniteQuery<T>>[0], 'queryKey' | 'queryFn' | 'initialPageParam' | 'getNextPageParam'>,
) {
  return useInfiniteQuery<T>({
    queryKey: [...key, limit],
    queryFn: ({ pageParam }) =>
      api.get<T>(path, { params: { limit, offset: pageParam as number } }),
    initialPageParam: 0,
    getNextPageParam: (lastPage: any, allPages) => {
      const totalFetched = allPages.length * limit
      return lastPage?.count > totalFetched ? totalFetched : undefined
    },
    ...options,
  })
}
