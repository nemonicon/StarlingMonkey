'use server';
import { redirect } from 'next/navigation';
export async function submitFixture(formData) {
  const value = String(formData.get('value') ?? '').slice(0, 64);
  redirect(`/action-result?value=${encodeURIComponent(value)}`);
}
