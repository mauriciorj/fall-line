"use client";

import {
  Mountain,
  Menu,
  Mail,
  HelpCircle,
  MessageCircle,
  FileText,
} from "lucide-react";
import { FilterPopover } from "./filterPopover";
import LocationDropdown from "./locationDropdown";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import useFilters from "@/hooks/useFilters";
import { useIsMobile } from "@/hooks/useMobile";

export function Header() {
  const isMobile = useIsMobile();

  const { filters, setFilters, isFiltersActive, handleClearFilters } =
    useFilters();

  return (
    <header className="sticky top-0 z-50 bg-card border-b border-border">
      <div className="px-6 py-4 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2 text-primary">
          <Mountain className="w-10 h-10" />
          <span className="text-2xl pt-2 font-bold tracking-wide uppercase">
            {!isMobile && "Ontario Ski Guide"}
          </span>
        </div>
        {isMobile ? (
          <div className="flex flex-col">
            <div className="w-full flex flex-row">
              <LocationDropdown setLocation={() => {}} />
              <Sheet>
                <SheetTrigger asChild>
                  <Button
                    variant="default"
                    size="icon"
                    className="h-9 w-25 ml-5"
                  >
                    <span>Menu</span>
                    <Menu className="h-4 w-4" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[280px]">
                  <SheetHeader>
                    <SheetTitle className="text-left">Menu</SheetTitle>
                  </SheetHeader>
                  <nav className="mt-6 flex flex-col gap-1">
                    <a
                      href="mailto:support@ontarioskiguide.com"
                      className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                    >
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      Contact Us
                    </a>
                    <a
                      href="#support"
                      className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                    >
                      <HelpCircle className="h-4 w-4 text-muted-foreground" />
                      Support
                    </a>
                    <a
                      href="#feedback"
                      className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                    >
                      <MessageCircle className="h-4 w-4 text-muted-foreground" />
                      Feedback
                    </a>
                    <a
                      href="#terms"
                      className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                    >
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      Terms & Privacy
                    </a>
                  </nav>
                </SheetContent>
              </Sheet>
            </div>
            <div className="w-full">
              <FilterPopover
                filters={filters}
                onChange={setFilters}
                isActive={isFiltersActive}
                onClear={handleClearFilters}
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-row">
            <LocationDropdown setLocation={() => {}} />
            <FilterPopover
              filters={filters}
              onChange={setFilters}
              isActive={isFiltersActive}
              onClear={handleClearFilters}
            />
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="default" size="icon" className="h-9 w-25 ml-5">
                  <span>Menu</span>
                  <Menu className="h-4 w-4" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[280px]">
                <SheetHeader>
                  <SheetTitle className="text-left">Menu</SheetTitle>
                </SheetHeader>
                <nav className="mt-6 flex flex-col gap-1">
                  <a
                    href="mailto:support@ontarioskiguide.com"
                    className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                  >
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    Contact Us
                  </a>
                  <a
                    href="#support"
                    className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                  >
                    <HelpCircle className="h-4 w-4 text-muted-foreground" />
                    Support
                  </a>
                  <a
                    href="#feedback"
                    className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                  >
                    <MessageCircle className="h-4 w-4 text-muted-foreground" />
                    Feedback
                  </a>
                  <a
                    href="#terms"
                    className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
                  >
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    Terms & Privacy
                  </a>
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        )}
      </div>
    </header>
  );
}
