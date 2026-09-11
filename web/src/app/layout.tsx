import React from 'react';

export const metadata = {
  title: 'Smart Medicine Platform — Admin & User Portal',
  description: 'Management, verification, analytics, and voice assistant portal.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
