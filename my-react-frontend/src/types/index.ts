export interface ApiResponse<T> {
    data: T;
    status: number;
    message: string;
}

export interface ExampleData {
    id: number;
    name: string;
    description: string;
}