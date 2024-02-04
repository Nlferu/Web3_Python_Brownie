/* eslint-disable spaced-comment */
/// <reference types="react-scripts" />

import { useEthers } from "@usedapp/core"
import { constants } from "ethers"
import { YourWallet } from "./yourWallet"
import { makeStyles } from "@material-ui/core"
import helperConfig from "../helper-config.json"
import networkMapping from "../chain-info/deployments/map.json"
import brownieConfig from "../brownie-config.json"
import dapp from "../dapp.png"
import eth from "../eth.png"
import dai from "../dai.png"

export type Token = {
    image: string
    address: string
    name: string
}

const useStyles = makeStyles((theme) => ({
    title: {
        color: theme.palette.common.black,
        textAlign: "center",
        padding: theme.spacing(4)
    }
}))

export const Main = () => {
    // Show token values from the wallet
    // Get the address of differen tokens
    // Get the balance of the users wallet
    // send the brownie-config to our `src` folder
    // send the build folder
    const classes = useStyles()
    const { chainId, error } = useEthers()
    // Below "tertiary operator: `?`" says if that below "chainId" exists use helperConfig, ":" means if it doesn't exists use "dev"  
    const networkName = chainId ? helperConfig[chainId] : "dev"
    let stringChainId = String(chainId)
    console.log(chainId)
    console.log(networkName)

    // Below Tokens Are Defined In "map.json"
    const dappTokenAddress = chainId ? networkMapping[stringChainId]["DappToken"][0] : constants.AddressZero
    // Below Tokens Are Defined In "brownie-config.json"
    const wethTokenAddress = chainId ? brownieConfig["networks"][networkName]["weth_token"] : constants.AddressZero
    const fauTokenAddress = chainId ? brownieConfig["networks"][networkName]["fau_token"] : constants.AddressZero

    const supportedTokens: Array<Token> = [
        {
            image: dapp,
            address: dappTokenAddress,
            name: "DAPP"
        },
        {
            image: eth,
            address: wethTokenAddress,
            name: "WETH"
        },
        {
            image: dai,
            address: fauTokenAddress,
            name: "DAI"
        }
    ]

    return (<>
        <h2 className={classes.title}>Dapp Token App</h2>
        <YourWallet supportedTokens={supportedTokens} />
    </>)
}
