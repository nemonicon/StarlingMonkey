import './globals.css';
export const metadata = { title: 'Starling Next Runtime Fixture', description: 'Deterministic App Router runtime compatibility fixture', icons: { icon: 'data:,' } };
export default function RootLayout({ children }) {
  return <html lang="en"><body><header data-testid="root-layout">NEXT_ROOT_LAYOUT</header><nav><a href="/">Home</a><a href="/nested/leaf">Nested</a><a href="/actions">Action</a><a href="/client">Counter</a><a href="/stream">Stream</a></nav><main>{children}</main></body></html>;
}
