import "./styles/globals.css";

export const metadata = {
  title: "MR.N Local Agent",
  description: "Local web automation agent"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
