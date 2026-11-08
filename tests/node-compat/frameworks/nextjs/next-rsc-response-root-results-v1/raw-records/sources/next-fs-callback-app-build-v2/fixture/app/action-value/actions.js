'use server';

export async function returnActionValue(_previous, formData) {
  const values = formData.getAll('value');
  const value = values[0];
  if (values.length !== 1 || typeof value !== 'string' ||
      value.length < 1 || value.length > 64 || /[^a-z0-9-]/.test(value)) {
    throw new Error('Exactly one bounded lowercase action value is required');
  }
  return value;
}
