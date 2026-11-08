import { redirect } from 'next/navigation';
export function GET() { redirect('/nested/leaf'); }
