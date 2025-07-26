import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive font-medieval",
  {
    variants: {
      variant: {
        default:
          "bg-amber-500 text-ink-black shadow border-2 border-amber-600 hover:bg-amber-400 hover:shadow-lg transform hover:-translate-y-0.5 font-semibold",
        destructive:
          "bg-ruby-red text-parchment-light shadow border-2 border-red-800 hover:bg-red-700 hover:shadow-lg transform hover:-translate-y-0.5",
        outline:
          "border-2 border-parchment-shadow bg-parchment-dark text-ink-black shadow hover:bg-parchment hover:text-ink-black transform hover:-translate-y-0.5",
        secondary:
          "bg-parchment-dark text-ink-black shadow border-2 border-parchment-shadow hover:bg-parchment transform hover:-translate-y-0.5",
        ghost:
          "hover:bg-parchment hover:text-ink-black border-2 border-transparent hover:border-parchment-shadow transform hover:-translate-y-0.5",
        link: "text-amber-700 underline-offset-4 hover:underline hover:text-amber-600",
        success: "bg-emerald-600 text-white shadow border-2 border-green-800 hover:bg-green-700 hover:shadow-lg transform hover:-translate-y-0.5"
      },
      size: {
        default: "h-10 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-12 rounded-md px-6 has-[>svg]:px-4 text-base",
        icon: "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }