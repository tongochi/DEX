import { request, Variables } from "graphql-request";

export const fetcher = (url: string, query: string, variables: Variables) =>
  request(url, query, variables);
