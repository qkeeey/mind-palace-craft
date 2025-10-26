import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Configure from "./pages/Configure";
import FloorTable from "./pages/FloorTable";
import Walkthrough from "./pages/Walkthrough";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/configure" element={<Configure />} />
          <Route path="/floors/:floorId" element={<FloorTable />} />
          <Route path="/floors/:floorId/walkthrough" element={<Walkthrough />} />
          <Route path="/rooms/:roomId/table" element={<FloorTable />} />
          <Route path="/rooms/:roomId/walkthrough" element={<Walkthrough />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
