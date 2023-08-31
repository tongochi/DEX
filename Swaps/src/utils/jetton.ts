// some feature which has not implemented fully, just parsing boc`s
import { Coins, Slice } from "ton3-core";
// import { BOC } from 'ton3-core'
// import { uintToHex } from "ton3-core/dist/utils/helpers";

// export enum JettonOps {
//   TRANSFER = "0xf8a7ea5",
//   TRANSFER_NOTIFICATION = "0x7362d09c",
//   INTERNAL_TRANSFER = "0x178d4519",
//   EXCESSES = "0xd53276db",
//   BURN = "0x595f07bc",
//   BURN_NOTIFICATION = "0x7bdd97de",
// }

export const loadTransferNotification = (
  body: Slice,
  payload: { opUint32Hex: string },
) => {
  const queryId = body.loadBigUint(64);
  const jettonAmount = body.loadCoins();
  const from = body.loadAddress();
  const forwardPayload = body.loadBit() ? Slice.parse(body.loadRef()) : body;

  return {
    ...payload,
    queryId,
    jettonAmount,
    from,
    forwardPayload,
  };
};

// export const parseBocBase64 = (bocBase64: string) => {
//   // 0x7362d09c - jetton transfer notification
//   const [deserialized] = BOC.from(bocBase64);
//   const slice = deserialized.slice();
//   const opUint32 = slice.loadUint(32);
//   const opUint32Hex = `0x${uintToHex(opUint32)}`;
//   console.log(opUint32, opUint32Hex);
//
//   if (opUint32Hex === JettonOps.TRANSFER) {
//     const queryId = slice.loadBigUint(64);
//     const amount = slice.loadCoins();
//
//     console.log(queryId, amount);
//   }
//
//   if (opUint32Hex === JettonOps.TRANSFER_NOTIFICATION) {
//     console.log(loadTransferNotification(slice, { opUint32Hex }));
//   }
//
//   if (opUint32Hex === JettonOps.EXCESSES) {
//     console.log("exc");
//     const queryId = slice.loadBigUint(64);
//     console.log(queryId);
//   }
// };

// parseBocBase64('te6cckECAwEAASkAAZy4BhDUtLNN7WHrok9mtfoNlW88tbDknxwNISF93aFRHvz2eJIYEbyXCavIET/6eLwQUlGXeKc+o5xSYvXQiXEBKamjF2StPBcAAAHcAAMBAdNiADt3BW0qwi2ouZa0VVtB+ItsTRR0reXdrNlHeXz4Q1KUIO5rKAAAAAAAAAAAAAAAAAAAD4p+pQAAAAAAADA5MBhqCADvO5kConGyoByJOKUjz+JOcYR6rramIAAe1Ep3rA5wnBA/LlEDAgDRJZOFYYAQ9yRINU1K++Yk4owYITipv7MTQ11AZewg+ljLrdEPOcEALL+ORb5p4vzy96Yimh59V//z6FNKD8JDrClmJ90l0NRwA7EHhSlJYfIhYxf+w8lAO49GOpLyOAhRF4lOxne6kIJKui5UtQ==');
export const coinsToNumber = (value: string, decimals?: number) => {
  if (value === "") return "";

  return Number(Coins.fromNano(value, decimals).toString()).toFixed(2);
};
