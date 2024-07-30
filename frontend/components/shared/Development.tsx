import React from "react";
import { Terminal } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
  } from "@/components/ui/accordion"
import { accordionItems } from "@/constants";

const Development = () => {
  return (
    <section className="wrapper flex flex-col gap-10 items-center justify-center">
        <h1 className="text-3xl font-bold ">Proccess ...</h1>
      <Alert variant="destructive">
        <Terminal className="h-4 w-4" />
        <AlertTitle>Under Development</AlertTitle>
        <AlertDescription>This feature is under development</AlertDescription>
      </Alert>

      <Accordion type="single" collapsible className="w-full">
        {accordionItems.map((item, i) => {
            return (
                <AccordionItem
                key={i}
                value={item.value}
                >
                    <AccordionTrigger>
                        {item.title}
                    </AccordionTrigger>
                    <AccordionContent>
                        {item.description}
                    </AccordionContent>
                </AccordionItem>
            )
        })}
      </Accordion>

    </section>
  );
};

export default Development;
