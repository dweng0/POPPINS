import React from "react";
import { Text } from "ink";

type AppProps = {
  name?: string;
};

export default function App({ name = "World" }: AppProps) {
  return (
    <Text>
      Hello, <Text color="green">{name}</Text>
    </Text>
  );
}
