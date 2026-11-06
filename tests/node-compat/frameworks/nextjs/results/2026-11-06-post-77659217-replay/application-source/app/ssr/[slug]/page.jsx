export const dynamic = 'force-dynamic';
export async function generateMetadata({ params }) { const { slug } = await params; return { title: `SSR ${slug}` }; }
export default async function SlugPage({ params }) {
  const { slug } = await params;
  return <section data-testid="ssr"><h1>NEXT_DYNAMIC_SSR</h1><p data-testid="slug">{slug}</p></section>;
}
