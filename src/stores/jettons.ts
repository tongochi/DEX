import { defineStore } from "pinia";
import { readonly, ref } from "vue";

type JettonSymbols = "jUSDT" | "STON";

type Jetton = {
  symbol: JettonSymbols;
  addressMinterBouncable: string;
  addressMinterRaw: string;
};

type Jettons = Jetton[];

type State = {
  entity: Jettons;
  leftToken?: Jetton;
  rightToken?: Jetton;
};

export const useJettonStore = defineStore("jettons", () => {
  const entity = ref<State["entity"]>([
    {
      symbol: "jUSDT",
      addressMinterBouncable:
        "EQBynBO23ywHy_CgarY9NK9FTz0yDsG82PtcbSTQgGoXwiuA",
      addressMinterRaw:
        "0:729C13B6DF2C07CBF0A06AB63D34AF454F3D320EC1BCD8FB5C6D24D0806A17C2",
    },
    {
      symbol: "STON",
      addressMinterBouncable:
        "EQA2kCVNwVsil2EM2mB0SkXytxCqQjS4mttjDpnXmwG9T6bO",
      addressMinterRaw:
        "0:3690254DC15B2297610CDA60744A45F2B710AA4234B89ADB630E99D79B01BD4F",
    },
  ]);

  const leftToken = ref<State["leftToken"]>(undefined);
  const rightToken = ref<State["rightToken"]>(undefined);

  const findJettonBySymbol = (symbol: JettonSymbols) => {
    return entity.value.find((jetton) => {
      if (jetton.symbol === symbol) {
        return jetton;
      }
    });
  };

  const leftTokenSet = (payload: State["leftToken"]) => {
    leftToken.value = payload;
  };

  const rightTokenSet = (payload: State["rightToken"]) => {
    rightToken.value = payload;
  };

  const leftTokenSwapToRightToken = () => {
    const left = leftToken.value;
    const right = rightToken.value;

    leftToken.value = right;
    rightToken.value = left;
  };

  return {
    entity: readonly(entity),
    leftToken,
    rightToken,
    findJettonBySymbol,
    leftTokenSet,
    rightTokenSet,
    leftTokenSwapToRightToken,
  };
});
