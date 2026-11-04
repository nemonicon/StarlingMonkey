// world root:component/root
export function identity(): string;
export function setup(caseId: number): string;
export function observe(caseId: number): string;
export function batch(caseId: number, operations: number): string;
export function checkpoint(): string;
export function stage(input: string): string;
export function validate(input: string): string;
