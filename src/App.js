import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import ConversationsList from './components/ConversationsList';
import ConversationView from './components/ConversationView';
import UploadForm from './components/UploadForm';
import Layout from './components/Layout';
import './App.css';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <ConversationsList />
      },
      {
        path: "upload",
        element: <UploadForm />
      },
      {
        path: "conversation/:id",
        element: <ConversationView />
      }
    ]
  }
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
