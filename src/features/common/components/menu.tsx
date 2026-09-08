import {
  FileText,
  Mail,
  Menu as MenuIcon,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const Menu = () => {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="default" size="icon" className="h-9 w-9 ml-5">
          <MenuIcon className="h-4 w-4" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[280px]">
        <SheetHeader>
          <SheetTitle className="text-left">Menu</SheetTitle>
        </SheetHeader>
        <nav className="mt-6 flex flex-col gap-1">
          <Link
            href="/contact"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <Mail className="h-4 w-4 text-muted-foreground" />
            Contact Us
          </Link>
          <Link
            href="/terms"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <FileText className="h-4 w-4 text-muted-foreground" />
            Terms of Service
          </Link>
          <Link
            href="/privacy"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            Privacy Policy
          </Link>
        </nav>
      </SheetContent>
    </Sheet>
  );
};

export default Menu;
