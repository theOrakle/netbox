# Netbox for Home Assistant

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/netbox-dark.svg">
    <img src="assets/netbox-light.svg" alt="NetBox" width="300">
  </picture>
</p>

Home Assistant integration for Netbox IPAM & DCIM.

It connects to your NetBox server with an API token (polled every 2 minutes) and creates one device with sensors for object totals, recent change counts, versions and script status, a script-error binary sensor, and an update entity showing whether a newer NetBox release exists.

# Installation

There are two main ways to install this custom component within your Home Assistant instance:

1. Using HACS (see https://hacs.xyz/ for installation instructions if you do not already have it installed):

   1. From within Home Assistant, click on the link to **HACS**
   2. Click the three-dot menu (⋮) in the top right corner and select **Custom repositories**
   3. Enter the URL for this repository in the section that says _Add custom repository URL_ and select **Integration** in the _Category_ dropdown list
   4. Click the **ADD** button
   5. Close the _Custom repositories_ window
   6. Search for **Netbox** in HACS and select it from the results (HACS uses a single unified search/filter list rather than separate category tabs)
   7. Click to download/install it, and proceed with any on-screen instructions
   8. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

2. Manual Installation:
   1. Download or clone this repository
   2. Copy the contents of the folder **custom_components/netbox** into the same file structure on your Home Assistant instance
      - An easy way to do this is using the [Samba add-on](https://www.home-assistant.io/getting-started/configuration/#editing-configuration-via-sambawindows-networking), but feel free to do so however you want
   3. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

While the manual installation above seems like less steps, it's important to note that you will not be able to see updates to this custom component unless you are subscribed to the watch list. You will then have to repeat each step in the process. By using HACS, you'll be able to see that an update is available and easily update the custom component.

# Configuration

There is a config flow for this integration. After installing the custom component:

1. Go to **Settings** → **Devices & services**
2. Click **+ Add integration** (bottom right) to set up a new integration
3. Search for **Netbox** and click on it
4. You will be guided through the rest of the setup process via the config flow

# Actions

This integration does not provide any actions. Control devices through the entities it creates (for example with the standard `switch`, `light`, `select` or `climate` actions).

# Removing the integration

1. Go to **Settings** → **Devices & services**, open **Netbox**, click the three-dot menu (⋮) next to the entry and choose **Delete**. The NetBox server entry, its devices and its entities are removed.
2. If you installed through HACS, open **HACS**, find **Netbox**, click the three-dot menu (⋮) and choose **Remove**. For a manual install, delete the **custom_components/netbox** folder instead.
3. Restart Home Assistant.

---
